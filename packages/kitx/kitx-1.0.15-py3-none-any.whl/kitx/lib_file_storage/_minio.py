import io
import warnings
import urllib3
from typing import Optional
from minio import Minio
from minio.datatypes import Object
from urllib3 import Retry
try:
    from urllib3.response import BaseHTTPResponse  # type: ignore[attr-defined]
except ImportError:
    from urllib3.response import HTTPResponse as BaseHTTPResponse

from urllib3.util import Timeout
from .func import FileStorageConfig
from .interface import ObjectInterface


class MinioImpl(ObjectInterface):


    def __init__(self, c: FileStorageConfig):
        self.bucket = c.fs_bucket

        http_pool = urllib3.PoolManager(
            timeout=Timeout(connect=c.fs_connect_timeout, read=c.fs_read_timeout),
            maxsize=10,
            retries=Retry(
                total=c.fs_retry_num,
                backoff_factor=0.2,
                status_forcelist=[500, 502, 503, 504]
            )
        )
        self.client = Minio(
            endpoint=c.fs_endpoint,
            access_key=c.fs_secret_id,
            secret_key=c.fs_secret_key,
            region=c.fs_region,
            secure=c.fs_secure,
            http_client=http_pool,
        )
        bucket_exists = self.client.bucket_exists(self.bucket)
        if not bucket_exists:
            self.client.make_bucket(self.bucket)

    def upload(self,
               file_path_name: str,
               bytes_io: io.BytesIO,
               length: Optional[int] = None,
               metadata: Optional[dict] = None,
               **kwargs):
        content_type = kwargs.get("content_type", "application/octet-stream")
        if length is None:
            length = len(bytes_io.getvalue())
        res = self.client.put_object(self.bucket, file_path_name, bytes_io, length, metadata=metadata,
                               content_type=content_type)
        return res.etag

    def download(self, file_path_name: str):
        response = None
        try:
            response = self.client.get_object(self.bucket, file_path_name)
            return response.read()
        finally:
            if response:
                response.close()
                response.release_conn()

    def object_exists(self, file_path_name: str) -> Optional[Object]:
        try:
            res: Object = self.client.stat_object(self.bucket, file_path_name)
            return res
        except Exception as e:
            warnings.warn(f"object_exists: {e}")
            return None
