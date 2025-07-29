import abc
import logging
import threading
from typing import List, Union, Dict, Optional, Any
from urllib.parse import urlparse

from airadar.tracking.model import (
    File,
    VersionStrategy,
    VersionItem1,
    StorageTypeItem,
    ResourceNameItem,
)

logger = logging.getLogger(__name__)

# Each thread gets its own storage instance. This offers a simplest way
# to avoid issues with boto3 and thread safety. The only issue is a bucket
# blocked in one thread could be re-tried again in a different thread. However, that
# should not cause too much overhead.
schema_to_storage_mapping = threading.local()


class URIComponents:
    schema: Optional[str] = None
    bucket: Optional[str] = None
    path: Optional[str] = None


class CloudStorage(abc.ABC):
    def __init__(self) -> None:
        self._blocked_buckets: set[str] = set()

    @abc.abstractmethod
    def get_files_for_uri(self, uri: str) -> Union[List[str], None]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_file_metadata(
        self,
        uri: str,
    ) -> Union[File, None]:
        raise NotImplementedError

    @staticmethod
    def parse_uri(uri: str) -> URIComponents:
        components = URIComponents()
        parsed_uri = urlparse(uri)
        components.schema = parsed_uri.scheme

        components.bucket = parsed_uri.netloc
        path = parsed_uri.path
        path = path.lstrip("/")
        components.path = path

        return components

    @staticmethod
    def get_storage_obj_for_uri(uri: str) -> Union[None, "S3Storage", "GCStorage"]:
        components = CloudStorage.parse_uri(uri)
        if not components.schema:
            return None

        return CloudStorage.get_storage_obj_for_uri_schema(components.schema)

    @staticmethod
    def get_storage_obj_for_uri_schema(
        schema: str,
    ) -> Union[None, "S3Storage", "GCStorage"]:
        if schema == "s3":
            if not hasattr(schema_to_storage_mapping, "s3_storage_obj"):
                s3_storage_obj = S3Storage()
                schema_to_storage_mapping.s3_storage_obj = s3_storage_obj

            if isinstance(schema_to_storage_mapping.s3_storage_obj, S3Storage):
                return schema_to_storage_mapping.s3_storage_obj
        elif schema == "gs":
            if not hasattr(schema_to_storage_mapping, "gc_storage_obj"):
                gs_storage_obj = GCStorage()
                schema_to_storage_mapping.gs_storage_obj = gs_storage_obj

            if isinstance(schema_to_storage_mapping.gs_storage_obj, GCStorage):
                return schema_to_storage_mapping.gs_storage_obj

        return None


class S3Storage(CloudStorage):
    def __init__(self) -> None:
        super().__init__()
        self.s3_client = None
        self.s3fs_client = None
        self._botocore = None

        self.s3_glob_available = True
        try:
            import boto3
            import botocore

            session = boto3.Session()
            self.s3_client = session.client("s3")
            self._botocore = botocore
        except ImportError as e:
            logger.error(
                """
                Failed to import boto3 module. Radar will not be able to fetch extra metadata for S3 buckets.\n
                You can install boto3 support using either: \n
                1. pip install boto3 \n
                2. pip install radar[aws]\n
                %s
                """,
                str(e),
            )

        try:
            import s3fs

            self.s3fs_client = s3fs.S3FileSystem()
        except:
            logger.info(
                "Failed to import s3fs module. Glob patterns for S3 will not be supported."
            )

    @staticmethod
    def file_from_s3_metadata(uri: str, response: Dict[str, Any]) -> File:
        f = File(uri=uri)

        f.size = response.get("ContentLength")
        version_id = response.get("VersionId")
        f.version = VersionItem1(root=str(version_id)) if version_id else None
        f.storage_type = StorageTypeItem(root="S3")
        f.version_strategy = VersionStrategy.s3

        return f

    def _get_files_for_glob(self, bucket: str, path: str) -> Union[None, List[str]]:
        if self.s3fs_client is None:
            return None

        try:
            detail_files = self.s3fs_client.glob(f"{bucket}/{path}", detail=True)
        except Exception as e:
            # s3fs swallows all exceptions from S3 (e.g. AccessDenied), so this only capture errors
            # from NoCredentialsError and other unexpected errors
            logger.error(
                "Unexpected error while trying to list files for glob pattern %s/%s: %s",
                bucket,
                path,
                str(e),
            )
            return None

        # This returns the fully qualified S3 path while excluding directories returned by glob
        return [
            f"s3://{key}"
            for key, details in detail_files.items()
            if details["type"] == "file"
        ]

    def _get_s3_uri(self, bucket: str, path: str) -> str:
        return f"s3://{bucket}/{path}"

    def get_files_for_uri(self, uri: str) -> Union[List[str], None]:
        if not self.s3_client:
            return None

        components = CloudStorage.parse_uri(uri)
        schema = components.schema
        bucket = components.bucket
        path = components.path

        logger.debug(
            "Processing request for S3: schema=%s, bucket=%s, path=%s",
            schema,
            bucket,
            path,
        )

        if schema != "s3":
            logger.debug(f"Invalid URI schema for an S3 path: %s")
            return None

        if not bucket:
            logger.debug(f"Invalid URI schema for an S3 path: %s")
            return None

        if bucket in self._blocked_buckets:
            logger.debug(
                f"Requested bucket %s is blacklisted because of previous error in accessing it",
                components.bucket,
            )
            return None

        path = components.path or ""

        # If a customer wants to add files with a literal "*" or "?" in their keys,
        # this approach may cause unexpected behavior.
        # Discussed in https://github.com/protectai/airadar/issues/78
        if "*" in path or "?" in path or ("[" in path and "]" in path):
            return self._get_files_for_glob(bucket, path)

        files: List[str] = []
        continuation_token = None

        try:
            while True:
                if continuation_token is None:
                    response = self.s3_client.list_objects_v2(
                        Bucket=bucket,
                        Prefix=path,
                    )
                    if not "Contents" in response:
                        logger.warning("No files found in S3 for URI %s", uri)
                        return files
                else:
                    response = self.s3_client.list_objects_v2(
                        Bucket=bucket,
                        Prefix=path,
                        ContinuationToken=continuation_token,
                    )

                content_list = response.get("Contents", [])
                files.extend(
                    [
                        self._get_s3_uri(bucket, content["Key"])
                        for content in content_list
                    ]
                )

                # NextContinuationToken is only defined in response if IsTruncated is True
                # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/list_objects_v2.html
                if response.get("IsTruncated", False) == False:
                    break
                else:
                    continuation_token = response.get("NextContinuationToken", None)

            return files
        except Exception as e:
            if (
                self._botocore
                and isinstance(e, self._botocore.exceptions.ClientError)
                and e.response["Error"]["Code"] == "AccessDenied"
            ):
                self._blocked_buckets.add(bucket)
                logger.error(
                    "Access denied for URI %s. Adding bucket %s to block list.",
                    uri,
                    bucket,
                )
                return None

            logger.error(
                "Unexpected error while trying to list files for URI %s: %s",
                uri,
                str(e),
            )
            return None

    def get_file_metadata(self, uri: str) -> Union[File, None]:
        if not self.s3_client:
            return None

        components = self.parse_uri(uri)

        bucket = components.bucket
        path = components.path

        if not bucket or not path:
            return None

        try:
            response = self.s3_client.head_object(Bucket=bucket, Key=path)
            metadata = S3Storage.file_from_s3_metadata(uri, response)
            metadata.resource_name = ResourceNameItem(root=bucket)
            return metadata

        except Exception as e:
            if (
                self._botocore
                and isinstance(e, self._botocore.exceptions.ClientError)
                and e.response["Error"]["Code"] == "AccessDenied"
            ):
                self._blocked_buckets.add(bucket)
                logger.error(
                    "Access denied for URI %s. Adding bucket %s to block list.",
                    uri,
                    bucket,
                )
                return None

            logger.error(
                "Unexpected error while trying to retrieve file metadata for URI %s: %s",
                uri,
                str(e),
            )
            return None


class GCStorage(CloudStorage):
    def __init__(self) -> None:
        super().__init__()
        self.storage_client = None
        _gcs_sdk_available = False
        try:
            from google.cloud import storage

            _gcs_sdk_available = True
        except ImportError as e:
            logger.error(
                """
                Failed to import google-cloud-storage module. Radar will not be able to fetch extra metadata for GS buckets.\n
                You can install google-cloud-storage support using either: \n
                1. pip install google-cloud-storage \n
                2. pip install radar[gc]\n
                %s
                """,
                str(e),
            )

        if _gcs_sdk_available:
            from google.auth.exceptions import DefaultCredentialsError

            try:
                self.storage_client = storage.Client()
            except DefaultCredentialsError as e:
                logger.error(
                    """
                    Failed to authenticate with google cloud. Metadata from GCS will not be available.\n
                    You can set the path to service account json file by setting the environment variable for GOOGLE_APPLICATION_CREDENTIALS_PATH.
                    %s
                    """,
                    str(e),
                )
            except Exception as e:
                logger.error(
                    "Unknown error when trying to create google storage client: %s",
                    str(e),
                )

    @staticmethod
    def file_from_gcs_metadata(uri: str, response: Any) -> File:
        f = File(uri=uri)
        f.resource_name = ResourceNameItem(root=response.bucket.name)
        f.size = response.size
        f.storage_type = StorageTypeItem(root="GCS")
        if response.md5_hash:
            f.version = VersionItem1(root=response.md5_hash)
            f.version_strategy = (
                VersionStrategy.custom
            )  # TODO Add md5 on the API side first
        elif response.crc32c:
            f.version = VersionItem1(root=response.crc32c)
            f.version_strategy = (
                VersionStrategy.custom
            )  # TODO Add crc32 on the API side first
        else:
            f.version = VersionItem1(root=response.etag)
            f.version_strategy = (
                VersionStrategy.custom
            )  # TODO Add gsc on the API side first

        return f

    def get_file_metadata(self, uri: str) -> Union[File, None]:
        if not self.storage_client:
            return None
        from google.cloud.exceptions import NotFound, Forbidden
        from google.cloud.storage import Blob

        components = self.parse_uri(uri)

        bucket = components.bucket
        path = components.path

        if not bucket or not path:
            return None

        try:
            bucket_obj = self.storage_client.get_bucket(bucket)
            blob = bucket_obj.get_blob(path)
            if isinstance(blob, Blob):
                return GCStorage.file_from_gcs_metadata(uri, blob)

        except NotFound as e:
            logger.error(
                "Bucket not found for uri: %s\n%s",
                uri,
                str(e),
            )
            self._blocked_buckets.add(bucket)
            return None
        except Forbidden as e:
            logger.error("403 Forbidden for uri: %s\n%s", uri, str(e))
            self._blocked_buckets.add(bucket)
            return None
        except Exception as e:
            logger.error("Unknown error for uri: %s\n%s", uri, str(e))
            self._blocked_buckets.add(bucket)
            return None

        return None

    def get_files_for_uri(self, uri: str) -> Union[List[str], None]:
        if not self.storage_client:
            return None

        from google.cloud.exceptions import NotFound, Forbidden

        components = CloudStorage.parse_uri(uri)
        schema = components.schema
        bucket = components.bucket
        path = components.path

        logger.debug(
            "Processing request for GCS: schema=%s, bucket=%s, path=%s",
            schema,
            bucket,
            path,
        )

        if schema != "gs":
            logger.debug(f"Invalid URI schema for an GS path: %s")
            return None

        if not bucket:
            logger.debug(f"Invalid URI schema for an GS path: %s")
            return None

        if bucket in self._blocked_buckets:
            logger.debug(
                f"Requested bucket %s is blacklisted because of previous error in accessing it",
                components.bucket,
            )
            return None

        path = components.path or ""

        files: List[str] = []

        try:
            bucket_obj = self.storage_client.get_bucket(bucket)
            # If a customer wants to add files with a literal "*" or "?" in their keys,
            # this approach may cause unexpected behavior.
            # Discussed in https://github.com/protectai/airadar/issues/78
            ret = None
            if "*" in path or "?" in path or ("[" in path and "]" in path):
                ret = bucket_obj.list_blobs(match_glob=path)
            else:
                ret = bucket_obj.list_blobs(prefix=path)

            if not ret:
                logger.warning("No files found in GS for URI %s", uri)
                return files

            # GCS SDK returns an iterator that seems to handle pagination.
            for blob in ret:
                files.append(f"gs://{blob.bucket.name}/{blob.name}")

            return files
        except Forbidden as e:
            logger.error("403 Forbidden for uri: %s\n%s", uri, str(e))
            self._blocked_buckets.add(bucket)
            return None
        except NotFound as e:
            logger.error(
                "Requested bucket for %s was not found\n%s",
                uri,
                str(e),
            )
            self._blocked_buckets.add(bucket)
            return None

        except Exception as e:
            logger.error(
                "Unexpected error while trying to list files for URI %s\n%s",
                uri,
                str(e),
            )
            return None

        return None
