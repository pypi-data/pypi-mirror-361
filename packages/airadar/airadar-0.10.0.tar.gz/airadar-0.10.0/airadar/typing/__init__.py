# mypy: disable-error-code="assignment,attr-defined"

from typing import TypeVar, Optional, Dict, Any, Union

# Annotated is only in typing module as of Python 3.9, earlier
# versions require importing from typing_extensions. Depending on the version of
# Python used, one line or the other will cause a type error, so we ignore both
try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated


class RadarResponse:
    """
    Represents a response from interacting with the Radar SDK.

    Arguments:
        http_status_code: Status code returned from the API, or None if no request to the API was made
        entity_uuid: UUID representing the entity that was created or modified in the API call if the request was
            successful, or None if the call failed
        json_response: JSON response data from the API specific to the created or updated entity if the request
            was made, or None if the call failed
        error_msg: Detailed error message if there was an error in the Radar SDK or API, or None if the call succeeded
    """

    def __init__(
        self,
        http_status_code: Optional[int] = None,
        entity_uuid: Optional[str] = None,
        json_response: Optional[Dict[str, Any]] = None,
        error_msg: Optional[str] = None,
    ):
        self._status_code = http_status_code
        self._entity_uuid = entity_uuid
        self._json_response = json_response
        self._error_msg = error_msg

    @property
    def http_status_code(self) -> Optional[int]:
        return self._status_code

    @property
    def entity_uuid(self) -> Optional[str]:
        return self._entity_uuid

    @property
    def json_response(self) -> Optional[Dict[str, Any]]:
        return self._json_response

    @property
    def error_msg(self) -> Optional[str]:
        return self._error_msg

    @error_msg.setter
    def error_msg(self, msg: str) -> None:
        self._error_msg = msg

    def is_success(self) -> bool:
        """
        Helper method to tell if Radar request succeeded or not.

        Returns:
            True if the call succeeded, False otherwise
        """
        return self.entity_uuid is not None and self.error_msg is None


class BaseType:
    pass


class ArtifactType(BaseType):
    """
    Represents a generic machine learning artifact.

    Use one of the specific type of artifact radar.Model or radar.Dataset

    Arguments:
        type: Type of the artifact
        uri: The artifact's location on disk or cloud storage.
        metadata: Arbitrary key-value pairs describing the artifact.

    """

    def __init__(
        self,
        type: Optional[str] = None,
        uri: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.type = type
        self.uri = uri
        self.metadata = metadata


class DatasetType(ArtifactType):
    """
    Represent a machine learning dataset.

    Examples:
        ```
        @radar.pipeline(name="feature_generation")
        def feature_generation(dataset: radar.Dataset[pd.Dataframe]):
            ...
        ```
    """


class ModelType(ArtifactType):
    """
    Represent a machine learning model.
    """


class InputAnnotation:
    """A type to mark input artifact"""


class OutputAnnotation:
    """A type to mark output artifact"""


T = TypeVar("T")
TT = TypeVar("TT")

Artifact = Annotated[T, ArtifactType]
"""
A type to mark a variable as artifact

Arguments:
    T: Any type
"""


Dataset = Annotated[T, DatasetType]
"""
A type to mark a variable as dataset

Arguments:
    T: Any type

Examples:

    ```
    import pandas as pd

    @radar.pipeline(name="training")
    def training(train_data: radar.Dataset[pd.DataFrame])
        ...
    ```
"""

Model = Annotated[T, ModelType]
"""
A type to mark a variable as model

Arguments:
    T: Any type

Examples:

    ```
    import pandas as pd

    @radar.pipeline(name="training")
    def training(train_data: radar.Dataset[pd.DataFrame]) -> radar.Model
        ...
    ```
"""

Input = Annotated[TT, InputAnnotation]
"""
A type to indicate that the marked artifact is input.

Arguments:
    TT: ArtifactType, DatasetType, or ModelType
"""


Output = Annotated[TT, OutputAnnotation]
"""
A type to indicate that the marked artifact is input.

Arguments:
    TT: ArtifactType, DatasetType, or ModelType
"""

# Helper type for representing any of the 3 artifact types
AnyArtifact = Union[Dataset[Any], Model[Any]]
