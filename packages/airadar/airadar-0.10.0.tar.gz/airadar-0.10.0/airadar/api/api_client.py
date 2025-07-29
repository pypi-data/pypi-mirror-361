from __future__ import annotations

import abc
import requests
import json
import logging
import jwt
import importlib.metadata
from datetime import datetime
from concurrent.futures import Future
from typing import Union, Any, Optional, List, Dict
from pydantic import ValidationError, AnyUrl, PydanticUserError

from airadar.utils import get_git_info
from airadar.utils.config import airadar_configs, ConfigKeys
from airadar.utils.auth import get_ccf_access_token, get_private_key_access_token
from airadar.typing import RadarResponse
from airadar.tracking.model import (
    PipelineRunSchema,
    PipelineRunCreateRequestSchema,
    DatasetVersionCreateRequestSchema,
    DatasetSchema,
    ModelVersionCreateRequestSchema,
    ModelSchema,
    Dependency,
    File,
    PipelineSchema,
    PipelineCreateRequestSchema,
    PipelineRunState,
    PipelineRunUpdateRequestSchema,
    DeploymentCreateRequestSchema,
    DeploymentWithApplicationSchema,
    ExternalRunUrlItem,
    ApplicationUrlItem,
    BuildUrlItem,
    ExternalRunIdItem,
    DescriptionItem,
    RadarUri,
    VersionItem3,
    VersionItem,
    ExternalUrlItem,
    HardwareSchema,
)

logger = logging.getLogger(__name__)

try:
    RADAR_SDK_VERSION = importlib.metadata.version("airadar")
except importlib.metadata.PackageNotFoundError:
    RADAR_SDK_VERSION = "unknown"


class MissingAuthException(Exception):
    """Raised when the environment variables for obtaining access tokens are not set properly"""


class InvalidAuthTokenException(Exception):
    """Raised when we fail to obtain an access token from the auth provider"""


class AccessToken:
    def __init__(self, access_token: str):
        try:
            decoded_token = jwt.decode(
                access_token, options={"verify_signature": False}
            )
            self.expiration_timestamp = decoded_token.get("exp")
        except jwt.DecodeError:
            logger.critical("Failed to decode JWT access token")
            raise InvalidAuthTokenException("Access token is not valid")

        self.access_token = access_token

    def is_expired(self) -> bool:
        if not self.access_token or not self.expiration_timestamp:
            raise InvalidAuthTokenException("Access token is not valid")

        expiration_datetime = datetime.utcfromtimestamp(self.expiration_timestamp)
        return datetime.utcnow() > expiration_datetime


class HTTPClient(metaclass=abc.ABCMeta):
    def __init__(self) -> None:
        """
        Base class for api clients
        """
        self.base_url = str(airadar_configs.get_value(ConfigKeys.AIRADAR_API_SERVER))
        self.api_version_str = (
            airadar_configs.get_value(ConfigKeys.AIRADAR_API_VERSION) or "v1"
        )
        self.base_url = self.base_url.rstrip("/")

        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": f"radar-sdk-python/{RADAR_SDK_VERSION}",
        }

    @abc.abstractmethod
    def post(self, end_point: str, json_data: str) -> Union[Future[Any], RadarResponse]:
        """
        Abstract method for a HTTP POST call. Derived classes should implement this method.

        Arguments:
            end_point: End-point at the base_url
            json_data: JSON payload

        Returns:
            Either an [APIResponse][airadar.api.api_client.APIResponse] or a Future in case of async request.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def patch(
        self, end_point: str, json_data: str
    ) -> Union[Future[Any], RadarResponse]:
        """
        Abstract method for a HTTP PATCH call. Derived classes should implement this method.

        Arguments:
            end_point: End-point at the base_url
            json_data: JSON payload

        Returns:
            Either an [APIResponse][airadar.api.api_client.APIResponse] or a Future in case of async request.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, end_point: str) -> Union[Future[Any], RadarResponse]:
        """
        Abstract method for a HTTP GET call. Derived classes should implement this method.

        Arguments:
            end_point: End-point at the base_url

        Returns:
            Either an [APIResponse][airadar.api.api_client.APIResponse] or a Future in case of async request.
        """
        raise NotImplementedError


class SyncHTTPClient(HTTPClient):
    def __init__(self) -> None:
        super().__init__()
        self.jwt_access_token: AccessToken = SyncHTTPClient.fetch_access_token()

    @staticmethod
    def fetch_access_token() -> AccessToken:
        auth_client_url = airadar_configs.get_value(ConfigKeys.AIRADAR_AUTH_TENANT_URL)
        auth_client_id = airadar_configs.get_value(ConfigKeys.AIRADAR_AUTH_CLIENT_ID)
        auth_client_secret = airadar_configs.get_value(
            ConfigKeys.AIRADAR_AUTH_CLIENT_SECRET
        )
        auth_private_key = airadar_configs.get_value(
            ConfigKeys.AIRADAR_AUTH_CLIENT_PRIVATE_KEY
        )
        auth_key_id = airadar_configs.get_value(ConfigKeys.AIRADAR_AUTH_CLIENT_KID)
        auth_client_scope = airadar_configs.get_value(
            ConfigKeys.AIRADAR_AUTH_CLIENT_SCOPE
        )

        if (
            auth_client_url is None
            or auth_client_id is None
            or auth_client_scope is None
        ):
            raise MissingAuthException("Auth configurations are missing")

        # Prefer private key auth, otherwise fallback to client credential flow
        if auth_private_key is not None and auth_key_id is not None:
            logger.debug("Using private key auth strategy")
            access_token = get_private_key_access_token(
                str(auth_client_url),
                str(auth_client_id),
                str(auth_private_key),
                str(auth_key_id),
                str(auth_client_scope),
            )
        elif auth_client_secret is not None:
            logger.debug("Using client credential flow auth strategy")
            access_token = get_ccf_access_token(
                str(auth_client_url),
                str(auth_client_id),
                str(auth_client_secret),
                str(auth_client_scope),
            )
        else:
            raise MissingAuthException("Auth configurations are missing")

        if access_token is None:
            logger.critical(
                f"""
                Failed to obtain an access token. Check the logs for more information. 
                Make sure env variables are properly set.
                """
            )
            raise InvalidAuthTokenException("Failed to obtain an access token")

        logger.debug("Obtained a valid access token from auth provider")
        return AccessToken(access_token)

    def _handle_http_method(
        self, method: str, end_point: str, json_data: Optional[str] = None
    ) -> RadarResponse:
        try:
            logger.debug("Checking for a valid access token")
            if not self.jwt_access_token:
                self.jwt_access_token = SyncHTTPClient.fetch_access_token()
            elif self.jwt_access_token.is_expired():
                self.jwt_access_token = SyncHTTPClient.fetch_access_token()
        except (InvalidAuthTokenException, MissingAuthException) as e:
            error_msg = f"Failed to make {method} call due to invalid access token: {e}"
            logger.warning(error_msg)
            return RadarResponse(error_msg=error_msg)

        end_point = end_point.lstrip("/")
        url = f"{self.base_url}/{self.api_version_str}/{end_point}"
        logger.debug("Initiating %s request to endpoint %s", method, url)

        # urllib allows opening both http:// and file:// URLs. To avoid the security risk of
        # accidentally opening the latter, we need to validate the URL is an HTTP endpoint
        if not url.lower().startswith("http"):
            error_msg = f"Invalid URL {url} passed to post_json, skipping request"
            logger.warning(error_msg)
            return RadarResponse(error_msg=error_msg)

        func = None
        try:
            func = getattr(requests, method)
        except AttributeError as ae:
            error_msg = f"HTTP requested method is not part of requests library. {ae}"
            logger.exception(error_msg)
            return RadarResponse(error_msg=error_msg)

        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.jwt_access_token.access_token}",
        }
        try:
            resp = None
            if json_data:
                resp = func(
                    url=url,
                    json=json.loads(json_data),
                    headers=headers,
                    timeout=10,
                )
            else:
                resp = func(url=url, headers=self.headers, timeout=10)

            resp.raise_for_status()
            resp_json = resp.json()
            entity_uuid = resp_json.get("uuid")
            if entity_uuid is None:
                error_msg = f"Could not get entity UUID from response body: {resp_json}"
                logger.error(error_msg)
                return RadarResponse(
                    http_status_code=resp.status_code, error_msg=error_msg
                )

            return RadarResponse(
                http_status_code=resp.status_code,
                entity_uuid=entity_uuid,
                json_response=dict(resp_json),
            )
        except json.decoder.JSONDecodeError as e:
            error_msg = f"Error parsing json payload for request to {url}: {str(e)}"
            logger.error(error_msg)
            return RadarResponse(error_msg=error_msg)
        except requests.exceptions.HTTPError as e:
            if e.response is None:
                return RadarResponse(error_msg="Unknown HTTP Error occurred")
            error_msg = str(
                f"Error with request: {e.response.status_code}\n{e.response.text}"
            )
            logger.error(error_msg)
            return RadarResponse(
                http_status_code=e.response.status_code, error_msg=error_msg
            )
        except requests.exceptions.JSONDecodeError as e:
            error_msg = f"Response was not valid JSON for request to {url}: {str(e)}"
            logger.error(error_msg)
            return RadarResponse(http_status_code=500, error_msg=error_msg)
        except requests.exceptions.Timeout as e:
            error_msg = f"Request timed out for request to {url}"
            logger.error(error_msg)
            return RadarResponse(http_status_code=408, error_msg=error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during request to {url}: {str(e)}"
            logger.error(error_msg)
            status_code = None
            if (
                hasattr(e, "response")
                and hasattr(e.response, "status_code")
                and isinstance(e.response.status_code, int)
            ):
                status_code = e.response.status_code
            return RadarResponse(http_status_code=status_code, error_msg=error_msg)

    def post(self, end_point: str, json_data: str) -> RadarResponse:
        return self._handle_http_method("post", end_point, json_data)

    def patch(self, end_point: str, json_data: str) -> RadarResponse:
        return self._handle_http_method("patch", end_point, json_data)

    def get(self, end_point: str) -> RadarResponse:
        return self._handle_http_method("get", end_point)


class RadarAPIClient:
    def __init__(self) -> None:
        self.http_client = self._setup_http_client()

    def _setup_http_client(self) -> Union[SyncHTTPClient, None]:
        try:
            return SyncHTTPClient()
        except (InvalidAuthTokenException, MissingAuthException):
            pass
        except Exception as e:
            logger.critical(
                "Unexpected error when fetching Radar access token: %s", str(e)
            )

        return None

    def is_authorized(self) -> bool:
        return self.http_client is not None

    def _validate_api_response(
        self,
        response: RadarResponse,
        model_class: Any,
    ) -> RadarResponse:
        try:
            model_class.model_validate(response.json_response)
        except ValidationError as e:
            error_msg = "Got an invalid response from the API server"
            logger.critical(
                error_msg,
                e,
                exc_info=True,
            )
            return RadarResponse(
                http_status_code=response.http_status_code,
                error_msg=error_msg,
                json_response=response.json_response,
            )

        return response

    def post_pipeline(
        self, pipeline_name: str, external_url: Optional[ExternalUrlItem] = None
    ) -> RadarResponse:
        if self.http_client is None:
            return RadarResponse(error_msg="Client data collection disabled")

        try:
            pipeline_create_obj = PipelineCreateRequestSchema(
                name=pipeline_name, external_url=external_url
            )
        except (ValidationError, PydanticUserError) as e:
            error_msg = "Failed to pipeline create request object."
            logger.critical(
                error_msg,
                e,
                exc_info=True,
            )
            return RadarResponse(error_msg=error_msg)

        pipeline_create_res = self.http_client.post(
            "/pipelines",
            pipeline_create_obj.model_dump_json(),
        )

        if not pipeline_create_res.is_success():
            logger.critical(
                "AI Radar pipeline could not be created, no data will be collected by AI Radar for this run"
            )
            return pipeline_create_res

        try:
            pipeline = PipelineSchema.model_validate(pipeline_create_res.json_response)
        except ValidationError as e:
            error_msg = "Got an invalid response from the API server for pipeline create request"
            logger.critical(
                error_msg,
                e,
                exc_info=True,
            )
            self.disable_data_collection = True
            return RadarResponse(
                http_status_code=pipeline_create_res.http_status_code,
                error_msg=error_msg,
                json_response=pipeline_create_res.json_response,
            )

        # Set the pipeline run id here to avoid duplicate calls when airadar.log_artifact() is called
        # following a call to airadar.active_run()
        self.pipeline_id = pipeline.uuid
        self.pipeline = pipeline
        return pipeline_create_res

    def post_pipeline_run(
        self,
        pipeline_id: str,
        external_run_id: Optional[str] = None,
        run_at: Optional[datetime] = None,
        run_uri: Optional[str] = None,
        dependency_report: List[Dependency] = [],
    ) -> RadarResponse:
        if self.http_client is None:
            return RadarResponse(error_msg="Client data collection disabled")

        git_info = get_git_info()

        try:
            # TODO: Populate platform with a meaningful name
            # See https://github.com/protectai/radar-sdk/issues/72
            create_run_obj = PipelineRunCreateRequestSchema(
                external_run_id=(
                    ExternalRunIdItem(root=external_run_id) if external_run_id else None
                ),
                external_run_url=(
                    ExternalRunUrlItem(root=AnyUrl(run_uri)) if run_uri else None
                ),
                dependencies=dependency_report,
                run_at=run_at or datetime.now(),
                git_info=git_info,
            )
        except (ValidationError, PydanticUserError) as e:
            error_msg = "Error when trying to create request based on given inputs."
            logger.critical(
                error_msg,
                e,
                exc_info=True,
            )
            return RadarResponse(error_msg=error_msg)

        run_create_res = self.http_client.post(
            f"/pipelines/{pipeline_id}/runs",
            create_run_obj.model_dump_json(),
        )

        if not run_create_res.is_success():
            logger.critical(
                "AI Radar pipeline run ID could not be retrieved, no data will be collected by AI Radar for this run"
            )
            return run_create_res

        try:
            pipeline_run = PipelineRunSchema.model_validate(
                run_create_res.json_response
            )
        except ValidationError as e:
            error_msg = "Got an invalid response from the API server for pipeline run create request"
            logger.critical(
                error_msg,
                e,
                exc_info=True,
            )
            self.disable_data_collection = True
            return RadarResponse(
                http_status_code=run_create_res.http_status_code,
                error_msg=error_msg,
                json_response=run_create_res.json_response,
            )

        # Set the pipeline run id here to avoid duplicate calls when airadar.log_artifact() is called
        # following a call to airadar.active_run()
        self.pipeline_run_id = pipeline_run.uuid
        self.pipeline_run = pipeline_run
        return run_create_res

    def patch_pipeline_run(
        self,
        status: PipelineRunState,
        pipeline_run_id: str,
        completed_at: Optional[datetime] = None,
    ) -> RadarResponse:
        if self.http_client is None:
            return RadarResponse(error_msg="Client data collection disabled")

        try:
            patch_run_obj = PipelineRunUpdateRequestSchema(
                status=status, completed_at=completed_at
            )
        except (ValidationError, PydanticUserError) as e:
            error_msg = "Error when trying to create request based on given inputs."
            logger.critical(
                error_msg,
                e,
                exc_info=True,
            )
            return RadarResponse(error_msg=error_msg)

        run_patch_res = self.http_client.patch(
            f"/pipelines/run/{pipeline_run_id}",
            patch_run_obj.model_dump_json(),
        )

        if not run_patch_res.is_success():
            logger.critical(
                f"Failed to mark pipeline run {pipeline_run_id} complete in AI Radar"
            )
            return run_patch_res

        try:
            patch_response = PipelineRunSchema.model_validate(
                run_patch_res.json_response
            )
            logger.info(
                f"Pipeline run with uuid={patch_response.uuid} updated successfully"
            )
            return run_patch_res
        except ValidationError as e:
            error_msg = "Got an invalid response from the API server for pipeline run patch request"
            logger.critical(
                error_msg,
                e,
                exc_info=True,
            )
            return RadarResponse(
                http_status_code=run_patch_res.http_status_code,
                error_msg=error_msg,
                json_response=run_patch_res.json_response,
            )

    def post_model(
        self,
        name: str,
        uri: str,
        files: List[File],
        version: Optional[str] = None,
        pipeline_run_id: Optional[str] = None,
        description: Optional[str] = None,
        properties: Optional[Dict[str, str]] = None,
        hardware: Optional[List[HardwareSchema]] = None,
    ) -> RadarResponse:
        if not self.http_client:
            return RadarResponse(error_msg="Client data collection disabled")

        if pipeline_run_id:
            model_version_endpoint = f"/pipelines/run/{pipeline_run_id}/model-versions"
        else:
            model_version_endpoint = "/models"

        try:
            request = ModelVersionCreateRequestSchema(
                name=name,
                external_uri=uri,
                version=VersionItem3(root=version) if version else None,
                description=DescriptionItem(root=description) if description else None,
                files=files,
                properties=properties,
                hardware=hardware if hardware else None,
            )
        except (ValidationError, PydanticUserError) as e:
            error_msg = "Error when trying to create request based on given inputs."
            logger.critical(
                error_msg,
                e,
                exc_info=True,
            )
            return RadarResponse(error_msg=error_msg)

        response = self.http_client.post(
            model_version_endpoint, request.model_dump_json(by_alias=True)
        )

        if not response.is_success():
            logger.critical(f"Failed to create model version for {name}")
            return response

        try:
            model_response = ModelSchema.model_validate(response.json_response)
            logger.info(f"Model version created with uuid={model_response.uuid}")
            return response
        except ValidationError as e:
            error_msg = "Got an invalid response from the API server for model version create request"
            logger.critical(
                error_msg,
                e,
                exc_info=True,
            )
            return RadarResponse(
                http_status_code=response.http_status_code,
                error_msg=error_msg,
                json_response=response.json_response,
            )

    def post_input_model(self, radar_uri: str, pipeline_run_id: str) -> RadarResponse:
        if not self.http_client:
            return RadarResponse(error_msg="Client data collection disabled")

        associate_model_endpoint = f"/pipelines/run/{pipeline_run_id}/associate-model"

        response = self.http_client.post(
            associate_model_endpoint, json.dumps({"radar_uri": radar_uri})
        )

        if not response.is_success():
            logger.critical(
                f"Failed to associate input model version at {radar_uri} with pipeline run {pipeline_run_id}"
            )
            return response

        try:
            model_response = ModelSchema.model_validate(response.json_response)
            if model_response.latest_version:
                logger.info(
                    f"Model version uuid={model_response.latest_version.uuid} was successfully associated with pipeline run {pipeline_run_id}"
                )
            return response
        except ValidationError as e:
            error_msg = f"Got an invalid response from the API server when trying to associate input model {radar_uri}"
            logger.critical(
                error_msg,
                e,
                exc_info=True,
            )
            return RadarResponse(
                http_status_code=response.http_status_code,
                error_msg=error_msg,
                json_response=response.json_response,
            )

    def post_dataset(
        self,
        name: str,
        uri: str,
        files: List[File],
        pipeline_run_id: str,
        version: Optional[str] = None,
        description: Optional[str] = None,
        hardware: Optional[List[HardwareSchema]] = None,
    ) -> RadarResponse:
        if not self.http_client:
            return RadarResponse(error_msg="Client data collection disabled")

        dataset_version_endpoint = f"/pipelines/run/{pipeline_run_id}/dataset-versions"

        try:
            request = DatasetVersionCreateRequestSchema(
                name=name,
                external_uri=uri,
                version=VersionItem(root=version) if version else None,
                description=DescriptionItem(root=description) if description else None,
                files=files,
                hardware=hardware if hardware else None,
            )
        except (ValidationError, PydanticUserError) as e:
            error_msg = "Error when trying to create request based on given inputs."
            logger.critical(
                error_msg,
                e,
                exc_info=True,
            )
            return RadarResponse(error_msg=error_msg)

        response = self.http_client.post(
            dataset_version_endpoint, request.model_dump_json()
        )

        if not response:
            logger.critical(f"Failed to create dataset version for {name}")
            return response

        try:
            dataset_response = DatasetSchema.model_validate(response.json_response)
            logger.info(f"Dataset version created with uuid={dataset_response.uuid}")
            return response
        except ValidationError as e:
            error_msg = "Got an invalid response from the API server for dataset version create request"
            logger.critical(
                error_msg,
                e,
                exc_info=True,
            )
            return RadarResponse(
                http_status_code=response.http_status_code,
                error_msg=error_msg,
                json_response=response.json_response,
            )

    def post_deployment(
        self,
        application_id: str,
        application_version: str,
        environment: str,
        application_url: Optional[str] = None,
        build_url: Optional[str] = None,
        radar_uris: Optional[List[str]] = None,
        build_time: datetime = datetime.now(),
    ) -> RadarResponse:
        if not self.http_client:
            return RadarResponse(error_msg="Client data collection disabled")

        try:
            deployment = DeploymentCreateRequestSchema(
                application_version=application_version,
                environment=environment,
                application_url=(
                    ApplicationUrlItem(root=AnyUrl(application_url))
                    if application_url
                    else None
                ),
                build_url=BuildUrlItem(root=AnyUrl(build_url)) if build_url else None,
                build_time=build_time,
                radar_uris=(
                    [RadarUri(root=radar_uri) for radar_uri in radar_uris]
                    if radar_uris
                    else []
                ),
            )
        except (ValidationError, PydanticUserError) as e:
            error_msg = "Error when trying to create request based on given inputs."
            logger.critical(
                error_msg,
                e,
                exc_info=True,
            )
            return RadarResponse(error_msg=error_msg)

        response = self.http_client.post(
            f"/applications/{application_id}/deployments",
            deployment.model_dump_json(),
        )
        if not response.is_success():
            logger.critical(
                f"Failed to create a deployment for application id {application_id}"
            )
            return response

        try:
            deployment_response = DeploymentWithApplicationSchema.model_validate(
                response.json_response
            )
            logger.info(f"Deployment created with uuid={deployment_response.uuid}")
            return response
        except ValidationError as e:
            error_msg = "Got an invalid response from the API server for deployment create request"
            logger.critical(
                error_msg,
                e,
                exc_info=True,
            )
            return RadarResponse(
                http_status_code=response.http_status_code,
                error_msg=error_msg,
                json_response=response.json_response,
            )
