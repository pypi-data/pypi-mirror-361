import os
import logging
from datetime import datetime

from typing import Dict, Union, Optional, List

from airadar import typing as radar_types
from airadar.typing import RadarResponse

from airadar.utils import (
    get_dependencies_from_environment,
    convert_hardware_dicts_to_schemas,
)
from airadar.api.api_client import RadarAPIClient
from airadar.tracking.model import (
    PipelineRunState,
    Dependency,
    ExternalUrlItem,
    HardwareSchema,
)
from airadar.utils import get_files_and_name_for_uri

logger = logging.getLogger(__name__)


class Radar:
    def __init__(self) -> None:
        self.radar_api_client = RadarAPIClient()
        if self.radar_api_client.is_authorized():
            self.disable_data_collection = False
        else:
            logger.error(
                "Authorization failed, disabling data collection for Radar instance"
            )
            self.disable_data_collection = True

    def log_artifact(
        self,
        uri: str,
        name: Union[str, None] = None,
        artifact_type: radar_types.AnyArtifact = radar_types.Model,
        description: Optional[str] = None,
        version: Optional[str] = None,
        properties: Optional[Dict[str, str]] = None,
        hardware: Optional[
            List[Union[HardwareSchema, Dict[str, Union[str, Dict[str, str], None]]]]
        ] = None,
    ) -> RadarResponse:
        """
        Log a collection of files from a given path as a model without pipeline.

        The base method for [log_dataset][airadar.radar.Radar.log_dataset] and
        [log_model][airadar.radar.Radar.log_model]

        Arguments:
            uri: URI of the artifact, without any schema prefix a local path is assumed. You can also specify glob pattern on local filesystem or cloud storage
                If a directory path is specified, all its contents will be recursively associated with this model.
            name: Human-readable name of the artifact.
                If None, the artifact directory path for multiple files or file name for the single file is used.
            artifact_type: Should be [Model][airadar.typing.Model] as we currently only support logging models without a pipeline.
            description: Human-readable description of the artifact
            version: A version string relevant to your environment. If no version string is applied. Radar will assign an auto-incremented numeric version
                to the artifact.
            properties: A dictionary of arbitrary key/value pairs that the user can provide for their own use cases.
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
                Radar API call to log the model or dataset version

        Examples:

        To log a dataset that was consumed as input by a given pipeline stage:
        ```
            import radar
            radar.log_artifact(
                uri="s3://bucket_name/training_data",
                name="flower_training_data",
                artifact_type=radar_types.Dataset,
            )
        ```
        """
        if artifact_type != radar_types.Model:
            error_msg = f"Only models can be logged without a pipeline context"
            logger.error(error_msg)
            return RadarResponse(error_msg=error_msg)

        if not uri or not isinstance(uri, str):
            error_msg = f"Artifact uri {uri} was empty or not of accepted type: str"
            logger.warning(error_msg)
            return RadarResponse(error_msg=error_msg)

        files, inferred_name = get_files_and_name_for_uri(uri)

        if not name:
            if not inferred_name:
                error_msg = f"Name for {uri} could not be inferred, provide a name for artifact to be logged"
                logger.warning(error_msg)
                return RadarResponse(error_msg=error_msg)

            name = inferred_name

        # Convert hardware dictionaries to schemas if needed
        hardware_schemas = None
        if hardware is not None:
            hardware_schemas = []
            for hw_item in hardware:
                if isinstance(hw_item, dict):
                    # Convert dict to HardwareSchema
                    converted_schemas = convert_hardware_dicts_to_schemas([hw_item])
                    hardware_schemas.extend(converted_schemas)
                else:
                    # Already a HardwareSchema
                    hardware_schemas.append(hw_item)

        radar_response = self.radar_api_client.post_model(
            name=name,
            uri=uri,
            files=files,
            description=description,
            version=version,
            properties=properties,
            hardware=hardware_schemas,
        )

        return radar_response

    def log_model(
        self,
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
        Log a model with associated files.

        Arguments:
            uri: URI of the model preferably belonging to a model with your model registry, without any schema prefix a local path is assumed.
                You can also specify glob pattern on local filesystem or cloud storage
                If a directory path is specified, all its contents will be recursively associated with this model.
            name: Human-readable name of the model this file is a part of.
                If None, the absolute filepath (for single file) or directory name (for directory path) is used.
            description: Human-readable description of the model. This is displayed on the Radar's model pages.
            version: A version string relevant to your environment. If no version string is applied. Radar will assign an auto-incremented numeric version
                to the model.
            properties: A dictionary of arbitrary key/value pairs that the user can provide for their own use cases.
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

        return self.log_artifact(
            uri, name, radar_types.Model, description, version, properties, hardware
        )

    def log_dataset(
        self,
        uri: str,
        name: Union[str, None] = None,
        description: Optional[str] = None,
        version: Optional[str] = None,
        hardware: Optional[
            List[Union[HardwareSchema, Dict[str, Union[str, Dict[str, str], None]]]]
        ] = None,
    ) -> RadarResponse:
        """
        Log a dataset with associated files.

        Arguments:
            path: URI of the dataset, without any schema prefix a local path is assumed.
                You can also specify glob pattern on local filesystem or cloud storage
                If a directory path is specified, all its contents will be recursively associated with this dataset
            name: Human-readable name of the dataset this file is a part of. If None, the absolute filepath is used.
            description: Human-readable description of the artifact
            version: Either a version string to be applied to all files associated with the logged dataset or a function which accepts a
                file's absolute path and returns a version string. If None, the SDK will attempt to infer the version for S3 resources.
            hardware: List of hardware information. Can be a list of HardwareSchema objects or dictionaries.
                Each dictionary should contain:
                - name (required): Name of the hardware
                - bom_ref (optional): BOM reference
                - version (optional): Version of the hardware
                - description (optional): Description of the hardware
                - manufacturer (optional): Manufacturer of the hardware
                - properties (optional): Additional properties as a dictionary

        A [RadarResponse][airadar.typing.RadarResponse] object with optional metadata from the
                Radar API call to log the dataset version
        """
        return self.log_artifact(
            uri=uri,
            name=name,
            artifact_type=radar_types.Dataset,
            description=description,
            version=version,
            hardware=hardware,
        )

    def log_deployment(
        self,
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
                application_uri="https://example.com/api/v1/service",
                build_uri="https://github.com/org/repo/actions/run/4",
                radar_uris=["radar://model/cost-predictions/latest"],
            )
            ```
        """
        if self.disable_data_collection:
            return RadarResponse(error_msg="Client data collection disabled")

        return self.radar_api_client.post_deployment(
            application_id=application_id,
            application_version=application_version,
            environment=environment,
            application_url=application_url,
            build_url=build_url,
            radar_uris=radar_uris,
            build_time=build_time,
        )


class RadarPipeline(Radar):
    def __init__(
        self,
        pipeline_id: Optional[str] = os.environ.get("AIRADAR_PIPELINE_ID"),
        editable: bool = False,
        external_run_id: Optional[str] = None,
        external_run_uri: Optional[str] = None,
        dependencies: Optional[List[Dependency]] = None,
        pipeline_name: Optional[str] = None,
        external_url: Optional[ExternalUrlItem] = None,
    ) -> None:
        super().__init__()

        self.pipeline_id = pipeline_id
        self.pipeline_name = pipeline_name
        self.pipeline_run_id: Optional[str] = None
        self.external_run_id = external_run_id
        self.external_run_uri = external_run_uri
        self.dependencies = dependencies
        self.props: Dict[str, Union[str, int, float, bool]] = {}
        self.editable = editable
        self.external_url = external_url

        if not self.pipeline_id and not self.pipeline_name:
            error_msg = "A Radar pipeline ID or name is required to initiate data collection session. Radar will not be able to collect any data"
            logger.critical(error_msg)
            self.disable_data_collection = True

    def start_run(self) -> RadarResponse:
        if self.disable_data_collection:
            return RadarResponse(error_msg="Data collection was disabled")

        if not self.pipeline_id:
            logger.info("No pipeline ID found, creating a new pipeline")

            if not self.pipeline_name:
                error_msg = "Pipeline name is required to create a new pipeline. Data collection will be disabled."
                logger.error(error_msg)
                return RadarResponse(error_msg=error_msg)

            response = self.radar_api_client.post_pipeline(
                pipeline_name=self.pipeline_name, external_url=self.external_url
            )

            if not response.is_success():
                logger.info(
                    "We couldn't create a new pipeline, disabling data collection"
                )
                self.disable_data_collection = True
                return response

            self.pipeline_id = response.entity_uuid
            logger.info("Obtained pipeline ID: %s", self.pipeline_id)

        # We should have pipeline id at this point either through user provided or obtained with name.
        if not self.pipeline_id:
            error_msg = "Pipeline ID is required to start a pipeline run. Data collection will be disabled."
            logger.error(error_msg)
            self.disable_data_collection = True
            return RadarResponse(error_msg=error_msg)

        if not self.dependencies:
            dependency_report = get_dependencies_from_environment()
        else:
            dependency_report = self.dependencies

        response = self.radar_api_client.post_pipeline_run(
            pipeline_id=self.pipeline_id,
            external_run_id=self.external_run_id,
            run_uri=self.external_run_uri,
            dependency_report=dependency_report,
        )

        if not response.is_success():
            self.disable_data_collection = True
            return response

        self.pipeline_run_id = response.entity_uuid

        return response

    def finish_run(self, failure: bool = False) -> RadarResponse:
        if not self.pipeline_run_id or self.disable_data_collection:
            return RadarResponse(error_msg="Finish run called on a non-active pipeline")

        completed_at = datetime.now()
        if failure:
            status = PipelineRunState.failed
        elif self.editable:
            status = PipelineRunState.active
        else:
            status = PipelineRunState.closed

        res = self.radar_api_client.patch_pipeline_run(
            status, self.pipeline_run_id, completed_at
        )

        self.disable_data_collection = True
        return res

    def log_artifact(
        self,
        uri: str,
        name: Union[str, None] = None,
        artifact_type: radar_types.AnyArtifact = radar_types.Model,
        description: Optional[str] = None,
        version: Optional[str] = None,
        properties: Optional[Dict[str, str]] = None,
        hardware: Optional[
            List[Union[HardwareSchema, Dict[str, Union[str, Dict[str, str], None]]]]
        ] = None,
    ) -> RadarResponse:
        """
        Log a collection of files from a given path as either model or dataset within a Radar pipeline.

        The base method for [log_dataset][airadar.radar.RadarPipeline.log_dataset]
        and [log_model][airadar.radar.RadarPipeline.log_model]

        Arguments:
            uri: URI of the artifact, without any schema prefix a local path is assumed. You can also specify glob pattern on local filesystem or cloud storage
                If a directory path is specified, all its contents will be recursively associated with this model.
            name: Human-readable name of the artifact.
                If None, the artifact directory path for multiple files or file name for the single file is used.
            artifact_type: Either of [Model][airadar.typing.Model] or [Dataset][airadar.typing.Dataset]. Model is the default.
            description: Human-readable description of the artifact
            version: A version string relevant to your environment. If no version string is applied. Radar will assign an auto-incremented numeric version
                to the artifact.
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
                Radar API call to log the model or dataset version

        Examples:

        To log a dataset that was consumed as input by a given pipeline stage:
        ```
            import radar
            radar.log_artifact(
                uri="s3://bucket_name/training_data.tar.gz",
                artifact_name="flower_training_data",
                artifact_type=radar_types.Dataset,
            )
        ```
        """

        if self.disable_data_collection:
            return RadarResponse(error_msg="Client data collection disabled")

        if not self.pipeline_run_id:
            error_msg = f"Active pipeline run is required to log an artifact. Did you call start_run()?"
            logger.error(error_msg)
            return RadarResponse(error_msg=error_msg)

        if artifact_type not in [radar_types.Dataset, radar_types.Model]:
            error_msg = f"Cannot log {name} of unsupported type {artifact_type}"
            logger.error(error_msg)
            return RadarResponse(error_msg=error_msg)

        if not uri or not isinstance(uri, str):
            error_msg = (
                f"Artifact uri {uri} was either empty or not an accepted type str"
            )
            logger.warning(error_msg)
            return RadarResponse(error_msg=error_msg)

        files, inferred_name = get_files_and_name_for_uri(uri)

        if not name:
            if not inferred_name:
                error_msg = f"Name for {uri} could not be inferred, provide a name for artifact to be logged"
                logger.warning(error_msg)
                return RadarResponse(error_msg=error_msg)

            name = inferred_name

        # Convert hardware dictionaries to schemas if needed
        hardware_schemas = None
        if hardware is not None:
            hardware_schemas = []
            for hw_item in hardware:
                if isinstance(hw_item, dict):
                    # Convert dict to HardwareSchema
                    converted_schemas = convert_hardware_dicts_to_schemas([hw_item])
                    hardware_schemas.extend(converted_schemas)
                else:
                    # Already a HardwareSchema
                    hardware_schemas.append(hw_item)

        if artifact_type == radar_types.Model:
            radar_response = self.radar_api_client.post_model(
                name=name,
                uri=uri,
                files=files,
                version=version,
                description=description,
                pipeline_run_id=self.pipeline_run_id,
                properties=properties,
                hardware=hardware_schemas,
            )
        elif artifact_type == radar_types.Dataset:
            if not self.pipeline_run_id:
                error_msg = f"Datasets can only be logged with an active pipeline run"
                logger.error(error_msg)

                return RadarResponse(error_msg=error_msg)

            radar_response = self.radar_api_client.post_dataset(
                name=name,
                uri=uri,
                files=files,
                pipeline_run_id=self.pipeline_run_id,
                description=description,
                version=version,
                hardware=hardware_schemas,
            )

        if not radar_response.is_success():
            self.disable_data_collection = True

        return radar_response

    def log_deployment(
        self,
        application_id: str,
        application_version: str,
        environment: str,
        application_uri: Optional[str] = None,
        build_uri: Optional[str] = None,
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
            application_uri: The URI to identify the application.
            build_uri: This is typically the URI of the CI/CD pipeline that is deploying the call.
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
                application_uri="https://example.com/api/v1/service",
                build_uri="https://github.com/org/repo/actions/run/4",
                radar_uris=["radar://model/cost-predictions/latest"],
            )
            ```
        """
        return RadarResponse(
            error_msg="log_deployment is only possible outside pipeline context"
        )

    def log_input_model(
        self,
        radar_uri: str,
    ) -> RadarResponse:
        """
        Log an existing Radar model to current pipeline run. This model will be associated as INPUT (base model) used by the pipeline.


        Arguments:
            radar_uri: Radar specific URI of the model. It takes the following format: radar://model/<model-name>/<model-version>

        Returns:
            A [RadarResponse][airadar.typing.RadarResponse] object with optional metadata from the
                Radar API call to log the model.

        Examples:

        To associate an model that was previously logged with Radar, find its URI from the Radar dashboard and log it as input:
        ```
            import airadar
            with airadar.active_run(pipeline_id="..") as radar:
                radar.log_input_model(
                    radar_uri="radar://model/credit risk score/v1",
                )
        ```
        """

        if self.disable_data_collection:
            return RadarResponse(error_msg="Client data collection disabled")

        if not self.pipeline_run_id:
            error_msg = f"Active pipeline run is required to log an input model. Did you call start_run()?"
            logger.error(error_msg)
            return RadarResponse(error_msg=error_msg)

        return self.radar_api_client.post_input_model(
            radar_uri=radar_uri, pipeline_run_id=self.pipeline_run_id
        )

    def is_closed(self) -> bool:
        return self.disable_data_collection
