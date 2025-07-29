import os
import logging
import logging.config
from datetime import datetime
from contextlib import contextmanager
from airadar import typing as radar_types
from typing import Union, Optional, List, Generator, Dict

from airadar.typing import RadarResponse
from airadar.radar import RadarPipeline, Radar
from airadar.tracking.model import Dependency, ExternalUrlItem, HardwareSchema

disable_datacollection_env_var = "DISABLE_RADAR_COLLECTION"
external_run_id_env_var = "AIRADAR_EXTERNAL_RUN_ID"
logger = logging.getLogger(__name__)

_global_radar_obj: Optional[Radar] = None


def log_model(
    uri: str,
    name: Union[str, None] = None,
    description: Optional[str] = None,
    version: Optional[str] = None,
    properties: Optional[Dict[str, str]] = None,
    hardware: Optional[
        List[Union[HardwareSchema, Dict[str, Union[str, Dict[str, str], None]]]]
    ] = None,
) -> RadarResponse:
    """
    Log a model with associated files without a pipeline. When creating artifacts
    within a pipeline use [active_run][airadar.tracking.fluent.active_run]

    Arguments:
        uri: URI to the model file, or the root directory, or glob pattern on local filesystem or cloud storage
            If a directory path is specified, all its contents will be recursively associated with this model.
        name: Human-readable name of the model this file is a part of.
            If None, the absolute filepath (for single file) or directory name (for directory path) is used.
        description: Human-readable description of the model. This is displayed on the Radar's model pages.
        version: Either a version string to be applied to all files associated with the logged model or a function which accepts a
            file's absolute path and returns a version string. If None, the SDK will attempt to infer the version for S3 resources.
        properties: Arbitrary key value properties that can be sent to the Radar console.
        hardware: List of hardware information. Can be a list of HardwareSchema objects or dictionaries.
            Each dictionary should contain:
            - name (required): Name of the hardware
            - bom_ref (optional): BOM reference
            - version (optional): Version of the hardware
            - description (optional): Description of the hardware
            - manufacturer (optional): Manufacturer of the hardware
            - properties (optional): Additional properties as a dictionary

    Returns:
        A [RadarResponse][airadar.typing.RadarResponse] object with optional metadata from the
            Radar API call to log the model version
    """
    global _global_radar_obj
    if _global_radar_obj is None:
        _global_radar_obj = Radar()

    return _global_radar_obj.log_artifact(
        uri=uri,
        name=name,
        artifact_type=radar_types.Model,
        description=description,
        version=version,
        properties=properties,
        hardware=hardware,
    )


def log_deployment(
    application_id: str,
    application_version: str,
    environment: str,
    application_url: Optional[str] = None,
    build_url: Optional[str] = None,
    radar_uris: Optional[List[str]] = None,
    build_time: datetime = datetime.now(),
) -> RadarResponse:
    """
    Creates a new deployment against an application.

    Deployments are used to monitor deployed models within applications running in a user's organization.
    These applications might include, but aren't limited to, inference applications that
    serve the model to other users or software.

    Ideally, you should integrate this call into your CI/CD pipeline responsible for deploying the model.
    The CI/CD pipelines can provide many of the arguments to this function.
    This information can then allow Radar to trace back the provenance of the model within your application

    Note: application_id is Radar specific unique identifier obtained from onboarding the
    application on Radar web console.

    Arguments:
        application_id: The uuid of the application obtained from Radar's console.
        application_version: The version of the application within users' environment.
        environment: The name of the environment e.g. production, staging, dev etc.
        application_url: The URI to identify the application.
        build_url: This is typically the URI of the CI/CD pipeline that is deploying the call.
        radar_uris: The URI of the model in the form of radar://model/<model-name>/<model-version>.
        build_time: The date and time at which the application was built e.g. injected by your CI/CD pipeline.

    Returns:
        A [RadarResponse][airadar.typing.RadarResponse] object with optional metadata from the
            Radar API call to log the deployment

    Example:
        ```
        import airadar
        airadar.log_deployment(
            application_id="..",
            application_version="1.0.5",
            environment="production",
            application_url="https://example.com/api/v1/service",
            build_url="https://github.com/org/repo/actions/run/4",
            radar_uris=["radar://model/cost-predictions/latest"],
        )
        ```
    """
    global _global_radar_obj
    if _global_radar_obj is None:
        _global_radar_obj = Radar()

    return _global_radar_obj.log_deployment(
        application_id=application_id,
        application_version=application_version,
        environment=environment,
        application_url=application_url,
        build_url=build_url,
        radar_uris=radar_uris,
        build_time=build_time,
    )


@contextmanager
def active_run(
    pipeline_id: Optional[str] = os.environ.get("AIRADAR_PIPELINE_ID"),
    external_run_id: Optional[str] = None,
    external_run_uri: Optional[str] = None,
    editable: bool = False,
    dependencies: Optional[List[Dependency]] = None,
    pipeline_name: Optional[str] = None,
    external_url: Optional[ExternalUrlItem] = None,
) -> Generator[RadarPipeline, None, None]:
    """
    Initialize a pipeline session to log ML artifacts dataset(s) and model(s) generated within a pipeline.

    Models and datasets logged within the context of an active run are associated with the pipeline whose ID was passed in to the
    active_run function. If no pipeline ID is passed, the ```AIRADAR_PIPELINE_ID``` environment variable will be used instead.

    The external_run_id can be used to tie together distributed runs of a pipeline. It tells Radar
    to combine metadata generated across several processes into a single pipeline run. You can pass
    the external run id through the active_run method or by setting ```AIRADAR_EXTERNAL_RUN_ID``` environment variable.

    In general, values provided explicitly to the active_run method will override values provided via environment variables.

    Arguments:
        pipeline_id: The uuid of the pipeline obtained from Radar's web dashboard.
        external_run_id: ID for a pipeline run provided by a 3rd party tool (e.g. MLflow or Kubeflow).
        external_run_uri: URI identifying this pipeline run from the platform it ran on.
        editable: To keep pipeline open to log additional artifacts to it, set this to True.
        dependencies: List of dependencies that the pipeline run depends on.
                        If not provided, the SDK will attempt to read python environment for dependencies
        pipeline_name: Name of the pipeline. It is used to create a new pipeline if pipeline_id is not provided.
        external_url: Link to external source of the pipeline.

    Returns:
        A [RadarPipeline][airadar.radar.RadarPipeline] object that defines interface into calling

    Example:
        ```
        import airadar
        with airadar.active_run(pipeline_id="....") as radar:
            radar.log_model(..)
            radar.log_dataset(..)
        ```
    """
    radar = None
    try:
        radar = RadarPipeline(
            pipeline_id=pipeline_id,
            editable=editable,
            external_run_id=external_run_id,
            external_run_uri=external_run_uri,
            dependencies=dependencies,
            pipeline_name=pipeline_name,
            external_url=external_url,
        )
        radar.start_run()
        yield radar
    except Exception as e:
        logger.error(
            "Unexpected exception during Radar pipeline active run: %s", str(e)
        )
        if radar:
            radar.finish_run(failure=True)

        raise e
    finally:
        if radar and not radar.is_closed():
            radar.finish_run()
