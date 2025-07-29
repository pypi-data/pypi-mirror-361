import logging
import threading
import time
import json
import os
from datetime import datetime

from typing import Optional, List

import airadar
from airadar.radar import Radar

logger = logging.getLogger(__name__)

mlflow_tracking_available = True

try:
    import mlflow
    from mlflow.tracking import MlflowClient
    from mlflow.entities import Run
except ImportError:
    logger.error(
        "Failed to import mlflow, tracking of mlflow artifacts will be disabled"
    )
    mlflow_tracking_available = False


def _find_all_model_artifacts(artifact_uri: str, artifacts: List[str]) -> List[str]:
    ml_model_paths = [path for path in artifacts if "MLmodel" in path]
    ret = []
    for ml_model_path in ml_model_paths:
        if "/" not in ml_model_path:
            continue
        ret.append(f"{artifact_uri}/{ml_model_path.split('/')[0]}")

    return ret


def _track_mlflow_current_run(run_id: str, timestamp: datetime) -> None:
    if run_id is None:
        return

    logger.info(f"AIRadar is now tracking the run: {run_id}")

    mlflow_run = None
    while True:
        mlflow_run = MlflowClient().get_run(run_id)
        if not mlflow_run:
            logger.warn(
                "Mlflow run_id was not valid. No further tracking will be done."
            )
            return

        if mlflow_run.info.status != "RUNNING":
            break

        time.sleep(5)  # TODO make this time configurable

    radar_pipeline_id = os.environ.get("AIRADAR_PIPELINE_ID")
    if not radar_pipeline_id:
        logger.warn(
            "A Radar pipeline ID is missing. Models from Mlflow will be logged without a pipeline"
        )
        _log_model_helper(Radar(), mlflow_run)
    else:
        with airadar.active_run(
            pipeline_id=radar_pipeline_id, external_run_id=mlflow_run.info.run_id
        ) as radar:
            _log_model_helper(radar, mlflow_run)
            for dataset_input in mlflow_run.inputs.dataset_inputs:
                source = dataset_input.dataset.source
                dataset_info = None
                try:
                    if source:
                        dataset_info = json.loads(source)
                except:
                    logger.info(
                        f"Got MLFlow dataset with source that we couldn't understand {source}"
                    )

                dataset_uri = None
                if dataset_info:
                    dataset_uri = dataset_info.get("url") or dataset_info.get("uri")

                if dataset_uri:
                    logger.info(
                        f"Logging a dataset from mlflow with uri = {dataset_uri}"
                    )
                    radar.log_dataset(dataset_uri, name=dataset_input.dataset.name)


def _log_model_helper(radar: Radar, mlflow_run: Run) -> None:
    model_versions = MlflowClient().search_model_versions(
        filter_string=f"run_id='{mlflow_run.info.run_id}'"
    )
    for model_version in model_versions:
        model_uri = f"models:/{model_version.name}/{model_version.version}"
        logger.info(
            f"Logging mlflow model from run {mlflow_run.info.run_id} with uri {model_uri}"
        )
        radar.log_model(
            model_uri, name=model_version.name, version=str(model_version.version)
        )


def _get_mlflow_run_id() -> None:
    run_id = None
    start_time = datetime.now()
    while True:
        if not mlflow.active_run() and not mlflow.last_active_run():
            time.sleep(1)  # TODO make this time configurable
        else:
            last_active_run = mlflow.last_active_run()
            if last_active_run:
                run_id = last_active_run.info.run_id
            break

    if run_id:
        logger.info("Got the mlflow run_id from the environment")
        tracking_thread = threading.Thread(
            target=_track_mlflow_current_run, args=(run_id, start_time), daemon=False
        )
        tracking_thread.start()


def start_mlflow_tracking(run_id: Optional[str] = None) -> None:
    """
    Track artifacts being logged to mlflow.

    if run_id is provided, the SDK will start tracking artifacts for the given run_id
    If run_id is not provided, the SDK waits until run_id of current run is available and then launch
        tracking of artifacts.

    Arguments:
        run_id: MLflow run id

    """

    # We start tracking with two threads, one is daemon thread that runs if there is no
    # run id provided, this thread then launches our second thread to gather artifacts.
    # If run_id is provided, we launch only the tracking thread.
    if not mlflow_tracking_available:
        logger.warn("Failed to import mlflow. Tracking is disabled")
        return

    if not run_id:
        # Temporarily making this a non-daemon thread. For very short mlflow code,
        # a daemon thread won't even get a chance to get the run-id. Since start_mlflow_tracking()
        # is only being called through mlflow run_context we will get the mlflow run_id eventually
        # TODO: Later can make this little more robust to do a final context flush if
        #       start_mlflow_tracking() was called.
        run_id_thread = threading.Thread(target=_get_mlflow_run_id, daemon=False)
        run_id_thread.start()
    else:
        tracking_thread = threading.Thread(
            target=_track_mlflow_current_run, args=(run_id,), daemon=False
        )
        tracking_thread.start()
