from typing import Union, List, Dict, Optional, Tuple
from types import FrameType
import os
import sys
from git import InvalidGitRepositoryError
from git.repo import Repo
from pathlib import Path
from urllib.parse import urlparse
from glob import glob

from airadar.tracking.model import (
    GitInfo,
    ShaItem,
    RepoUrlItem,
    RepoNameItem,
    RepoTypeItem,
    File,
    Dependency,
    License,
    LicenseWrapper,
    HardwareSchema,
    BomRefItem,
    VersionItem2,
    DescriptionItem,
    ManufacturerItem,
)
from airadar.tools.cloud_storage import CloudStorage
from airadar.extractors.dependency import (
    DependencyExtractor,
    PackageDependencyType,
)
import logging

logger = logging.getLogger(__name__)


def get_git_info() -> GitInfo:
    git_info = GitInfo()
    try:
        repo = Repo(search_parent_directories=True)
        sha = str(repo.head.object.hexsha)

        git_info.sha = ShaItem(root=sha)
        git_info.repo_url = RepoUrlItem(root=repo.remotes.origin.url)
        git_info.repo_name = RepoNameItem(
            root=repo.remotes.origin.url.split(".git")[0].split("/")[-1]
        )
        git_info.repo_type = RepoTypeItem(root="git")
        git_info.dirty = repo.is_dirty()
    except InvalidGitRepositoryError:
        logger.info("Not a valid git repo, no git metadata will be recorded")
        git_info.repo_type = RepoTypeItem(root="Unknown")
    except Exception as e:
        logger.warning("Failed to capture git context: %s", str(e))
        git_info.repo_type = RepoTypeItem(root="Unknown")

    return git_info


def get_calling_function_name() -> Union[str, None]:
    radar_logging_functions = [
        "log_artifact",
        "log_dataset",
        "log_model",
    ]
    try:
        frame: Optional[FrameType] = sys._getframe(0) or None
        in_radar_call_stack = False
        while frame:
            # We are within radar SDK function stack and can terminate the search as soon we reached
            # out of it.
            if (
                in_radar_call_stack
                and frame.f_code.co_name not in radar_logging_functions
            ):
                break

            # we are in user functions stack and will keep looking until a radar specific function is
            # found.
            if (
                not in_radar_call_stack
                and frame.f_code.co_name in radar_logging_functions
            ):
                in_radar_call_stack = True

            frame = frame.f_back

        if frame:
            # If code is executed in a Python file outside of a function, just use the filename
            if frame.f_code.co_name == "<module>":
                return os.path.basename(frame.f_code.co_filename)
            return frame.f_code.co_name
    except Exception as e:
        logger.warning("Failed to get calling function name: %s", str(e))

    return None


def name_artifact(artifact_path: Path) -> str:
    # Handle glob cases first - find nearest parent directory that contains no wildcards
    path_str = str(artifact_path)
    if "*" in path_str:
        parts = path_str.split("/")
        for part in reversed(parts):
            if "*" not in part and len(part) > 0:
                return part

    # Returns the parent directory or filename of Path
    return artifact_path.name


def update_file_metadata(files: List[File]) -> None:
    for file in files:
        if file.uri is None:
            continue

        storage_obj = CloudStorage.get_storage_obj_for_uri(file.uri)
        if not storage_obj:
            continue

        file_metadata = storage_obj.get_file_metadata(file.uri)
        if file_metadata is None:
            continue

        # Do not overwrite explicitly set version
        if file.version is None:
            file.version = file_metadata.version
            file.version_strategy = file_metadata.version_strategy

        file.resource_name = file_metadata.resource_name
        file.storage_type = file_metadata.storage_type
        file.size = file_metadata.size


def get_files_and_name_for_uri(
    uri: str,
) -> Tuple[List[File], Optional[str]]:
    artifact_list: List[str] = []
    inferred_name = None

    parsed_uri = urlparse(uri)

    storage_obj = CloudStorage.get_storage_obj_for_uri(uri)
    if storage_obj:
        inferred_name = name_artifact(Path(parsed_uri.path))
        file_list = storage_obj.get_files_for_uri(uri)
        if file_list is None:
            error_msg = f"Could not fetch file listing in cloud storage path: {uri}. Check radar.log for more details."
            logger.warning(error_msg)
        else:
            artifact_list.extend(file_list)
    else:
        if parsed_uri.scheme == "file" or not parsed_uri.scheme:
            root_dir = Path(parsed_uri.path)
            inferred_name = name_artifact(root_dir)

            if root_dir.is_file():
                artifact_list.append(str(root_dir))

            # If the user has provided a directory path, treat all contents of dir as matching
            elif root_dir.exists() and root_dir.is_dir():
                glob_list = root_dir.glob("**/*")
                matching_list = [str(artifact) for artifact in glob_list]
                # Filter for only files, not directories
                for match in matching_list:
                    if Path(match).is_file():
                        artifact_list.append(match)

            # Get list of matching files from user's input glob
            else:
                matching_list = glob(parsed_uri.path, recursive=True)
                # Filter for only files, not directories
                for match in matching_list:
                    if Path(match).is_file():
                        artifact_list.append(match)
        elif parsed_uri.scheme in ["runs", "models"]:
            # For now we just assume mlflow URIs, we can add additional check to detect model registry type with additional integs.
            # TODO: Check MLFLOW_TRACKING_URI is set

            from airadar.tools.model_registry import get_mlflow_model_info
            from airadar.tools.model_registry import get_mlflow_model_files

            model_version = get_mlflow_model_info(uri)
            if model_version:
                inferred_name = model_version.name
            else:
                inferred_name = "mlflow_model"

            if model_version and model_version.run_id:
                file_paths = get_mlflow_model_files(model_version.run_id)
                if file_paths:
                    artifact_list.extend(file_paths)
        else:
            logger.info(
                f"Radar currently doesn't know how to handle {uri}. We might only have limited metadata for this URI."
            )

    files: List[File] = []
    for path in artifact_list:
        files.append(File(uri=path))

    update_file_metadata(files)

    return files, inferred_name


# Create list of licenses in correct format and truncate names to 128 chars if longer.
def generate_license_list(licenses: List[Dict[str, str]]) -> List[LicenseWrapper]:
    return [
        LicenseWrapper(license=License(name=value[:128]))
        for license in licenses
        for key, value in license.items()
        if key == "name"
    ]


def get_dependencies_from_environment() -> List[Dependency]:
    dependency_list = []

    extractor = DependencyExtractor(PackageDependencyType.ENVIRONMENT)
    dependency_report = extractor.get_report()

    # Create dependency list with truncated values so users don't receive API pydcantic validation errors.
    dependency_components = dependency_report.get("components", [])
    for dependency_component in dependency_components:
        if dependency_component.get(
            "type", ""
        ) == "library" and dependency_component.get("name", ""):
            dependency_list.append(
                Dependency(
                    name=dependency_component.get("name", "")[:128],
                    version=dependency_component.get("version", "")[:256],
                    author=dependency_component.get("author", "")[:256],
                    purl=dependency_component.get("purl", "")[:256],
                    licenses=generate_license_list(
                        dependency_component.get("licenses", [])
                    ),
                )
            )

    return dependency_list


def convert_hardware_dicts_to_schemas(
    hardware_dicts: List[Dict[str, Union[str, Dict[str, str], None]]]
) -> List[HardwareSchema]:
    """
    Convert a list of hardware dictionaries to HardwareSchema objects.

    Args:
        hardware_dicts: List of dictionaries containing hardware information.
            Each dictionary should contain:
            - name (required): str - Name of the hardware
            - bom_ref (optional): str - BOM reference
            - version (optional): str - Version of the hardware
            - description (optional): str - Description of the hardware
            - manufacturer (optional): str - Manufacturer of the hardware
            - properties (optional): Dict[str, str] - Additional properties

    Returns:
        List[HardwareSchema]: List of HardwareSchema objects

    Raises:
        ValueError: If required fields are missing or invalid
    """
    hardware_schemas = []

    for i, hardware_dict in enumerate(hardware_dicts):
        if not isinstance(hardware_dict, dict):
            raise ValueError(f"Hardware item at index {i} must be a dictionary")

        # Validate required fields
        name = hardware_dict.get("name")
        if not name or not isinstance(name, str):
            raise ValueError(
                f"Hardware item at index {i} must have a 'name' field with a string value"
            )

        # Build the schema object with proper type handling
        bom_ref = None
        version = None
        description = None
        manufacturer = None
        properties = None

        # Handle optional fields with proper type wrapping
        if "bom_ref" in hardware_dict and hardware_dict["bom_ref"] is not None:
            bom_ref = BomRefItem(root=str(hardware_dict["bom_ref"]))

        if "version" in hardware_dict and hardware_dict["version"] is not None:
            version = VersionItem2(root=str(hardware_dict["version"]))

        if "description" in hardware_dict and hardware_dict["description"] is not None:
            description = DescriptionItem(root=str(hardware_dict["description"]))

        if (
            "manufacturer" in hardware_dict
            and hardware_dict["manufacturer"] is not None
        ):
            manufacturer = ManufacturerItem(root=str(hardware_dict["manufacturer"]))

        if "properties" in hardware_dict and hardware_dict["properties"] is not None:
            props = hardware_dict["properties"]
            if not isinstance(props, dict):
                raise ValueError(
                    f"Hardware item at index {i} 'properties' field must be a dictionary"
                )
            # Ensure all property values are strings
            properties = {str(k): str(v) for k, v in props.items()}

        hardware_schemas.append(
            HardwareSchema(
                name=name,
                bom_ref=bom_ref,
                version=version,
                description=description,
                manufacturer=manufacturer,
                properties=properties,
            )
        )

    return hardware_schemas
