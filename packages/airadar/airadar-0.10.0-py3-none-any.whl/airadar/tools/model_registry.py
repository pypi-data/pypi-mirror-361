import logging
from typing import Optional, List, Generator, Union
from urllib.parse import urlparse

mlflow_tracking_available = True

logger = logging.getLogger(__name__)

try:
    from mlflow.tracking import MlflowClient
    from mlflow.entities.model_registry import ModelVersion
except ImportError:
    logger.error(
        "Failed to import mlflow, tracking of mlflow artifacts will be disabled"
    )
    mlflow_tracking_available = False

from airadar.tools.cloud_storage import CloudStorage


def _find_all_model_artifacts(artifact_uri: str, artifacts: List[str]) -> List[str]:
    ml_model_paths = [path for path in artifacts if "MLmodel" in path]
    ret = []
    for ml_model_path in ml_model_paths:
        if "/" not in ml_model_path:
            continue
        ret.append(f"{artifact_uri}/{ml_model_path.split('/')[0]}")

    return ret


def _yield_mlflow_artifacts(
    client: MlflowClient, run_id: str, path: Optional[str] = None
) -> Generator[str, None, None]:
    for item in client.list_artifacts(run_id, path):
        if item.is_dir:
            yield from _yield_mlflow_artifacts(client, run_id, item.path)
        else:
            yield item.path


def get_mlflow_model_files(run_id: str) -> Optional[List[str]]:
    if not mlflow_tracking_available:
        logger.warn("Mlflow tracking is not available. Please install mlflow package.")
        return None

    if not run_id:
        logger.error("Need a valid run_id for fetching model(s) files from Mlflow")
        return None

    try:
        client = MlflowClient()
        mlflow_run = client.get_run(run_id)
        if not mlflow_run:
            logger.info(f"Mlflow run was not found {run_id}")
            return None

        artifacts = list(_yield_mlflow_artifacts(client, run_id))
        model_artifacts_uris = _find_all_model_artifacts(
            mlflow_run.info.artifact_uri, artifacts
        )

        files: List[str] = []
        for artifact_uri in model_artifacts_uris:
            storage_obj = CloudStorage.get_storage_obj_for_uri(artifact_uri)
            if storage_obj:
                file_list = storage_obj.get_files_for_uri(artifact_uri)
                if file_list:
                    files.extend(file_list)

        return files
    except Exception as e:
        logger.error(
            "Failed to fetch files for run_id %s: %s", run_id, e, exc_info=True
        )

    return None


def get_mlflow_model_info(mlflow_uri: str) -> Union["ModelVersion", None]:
    if not mlflow_tracking_available:
        logger.warning(
            "Mlflow tracking is not available. Please install mlflow package."
        )
        return None

    parsed_uri = urlparse(mlflow_uri)
    if parsed_uri.scheme not in ["runs", "models"]:
        return None

    mlflow_model_version = None

    mlflow_client = MlflowClient()

    if parsed_uri.scheme == "runs":
        run_id = None
        parts = parsed_uri.path.split("/")
        if len(parts) > 2:
            run_id = parts[1]

        if not run_id:
            logger.error(
                f"Mlflow URI {mlflow_uri} was not valid. It should be of format runs:/<run-id>/<run-name>"
            )
            return None

        model_versions = mlflow_client.search_model_versions(
            filter_string=f"run_id='{run_id}'"
        )
        # TODO: With runs we can have multiple models. The upstream code
        # need some modifications to handle this case. For now, we just picking
        # one model. Our Mlflow tracking plugin is handling multiple models in a run.
        if model_versions:
            mlflow_model_version = model_versions[0]
    else:
        # Only other possibility now is 'models:/' URI.
        name, version = None, None
        if "@" in parsed_uri.path:
            parts = parsed_uri.path.split("@")
            name, alias = parts[0][1:], parts[1]
            if name and alias:
                mlflow_model_version = mlflow_client.get_model_version_by_alias(
                    name=name, alias=alias
                )
            else:
                logger.debug("Failed to parse model name and alias from Mlflow URI")
        else:
            parts = parsed_uri.path.split("/")
            name, version = None, None
            if len(parts) > 2:
                name, version = parts[1], parts[2]

            if name and version:
                mlflow_model_version = mlflow_client.get_model_version(
                    name=name, version=version
                )
            else:
                logger.debug("Failed to parse model name and version from Mlflow URI")

    return mlflow_model_version
