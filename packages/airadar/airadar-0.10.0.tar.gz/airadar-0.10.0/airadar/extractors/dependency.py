import abc
import pathlib
import json
import logging
import importlib.metadata

from enum import Enum
from typing import Optional, Any, Dict

logger = logging.getLogger(__name__)


class Extractor(abc.ABC):
    @abc.abstractmethod
    def get_report(self) -> object:
        raise NotImplementedError


class PackageDependencyType(Enum):
    ENVIRONMENT = 1
    PIP_LOCK_FILE = 2
    POETRY_LOCK_FILE = 3
    REQUIREMENTS_TXT_FILE = 4
    CONDA_LIST_FILE = 5
    CONDA_EXPLICIT_LIST_FILE = 6


class SimpleEnvironmentParser:
    """
    A simplified parser that extracts package dependency information from
    the local Python environment.
    """

    def parse(self) -> Dict[str, Any]:
        """
        Parse the current Python environment and return information in a format
        compatible with the expected output structure.

        Returns:
            Dict containing package information in the expected format.
        """
        components = []

        # Use pkg_resources to get installed packages
        for dist in importlib.metadata.distributions():
            try:
                # Get package name and version
                package_name = dist.metadata["Name"]
                package_version = dist.version

                component: Dict[str, Any] = {
                    "type": "library",
                    "name": package_name,
                    "version": package_version,
                    "purl": f"pkg:pypi/{package_name}@{package_version}",
                    "author": "",
                    "licenses": [],
                }

                if "Author" in dist.metadata:
                    component["author"] = dist.metadata["Author"]
                elif "Author-email" in dist.metadata:
                    # Fall back to author email if author name is not available
                    component["author"] = (
                        dist.metadata["Author-email"].split("<")[0].strip()
                    )

                # Extract license information
                license_info = None
                if "License" in dist.metadata:
                    license_info = dist.metadata["License"]
                elif "Classifier" in dist.metadata:
                    # Try to extract license from classifiers if direct license not available
                    for classifier in dist.metadata.get_all("Classifier", []):
                        if classifier.startswith("License ::"):
                            license_parts = classifier.split(" :: ")
                            if len(license_parts) > 2:
                                license_info = license_parts[-1]
                                break

                # Format license information in the expected structure
                if license_info:
                    component["licenses"] = [{"name": license_info}]

                components.append(component)
            except Exception as e:
                logger.debug(f"Failed to extract package information for {dist}: {e}")
                continue

        return {"components": components}


class DependencyExtractor(Extractor):
    def __init__(
        self,
        package_type: PackageDependencyType,
        dependency_file_path: Optional[pathlib.Path] = None,
    ):
        if package_type != PackageDependencyType.ENVIRONMENT:
            raise NotImplementedError("Only environment extractor is available.")

        self._package_type = package_type
        self._dependency_file_path = dependency_file_path
        self.components = None

    def get_report(self) -> Dict[str, Any]:
        """
        Get dependency report.

        Returns:
            Dict containing the package information.
        """
        if self.components:
            return self.components

        parser = SimpleEnvironmentParser()
        dependency_report = parser.parse()

        return dependency_report
