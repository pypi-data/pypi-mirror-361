import io
from typing import Optional, ClassVar, Literal, Any
from ..__about__ import env_prefix
from .interface import ObjectInterface
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, model_validator
from enum import Enum


class FileStorageType(Enum):
    OSS = "oss"
    Minio = "minio"
    COS = "cos"


class FileStorageConfig(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(env_prefix=env_prefix,
                                                                    use_enum_values=True)

    # env "kitx_"
    fs_type: FileStorageType = Field(default=FileStorageType.COS.value)
    fs_endpoint: str = Field(default="cos.ap-guangzhou.myqcloud.com")
    fs_secret_id: str = Field(description="secret_id")
    fs_secret_key: str = Field(description="secret_key")
    fs_bucket: str = Field(description="secret_key")
    fs_scheme: str = Field(default="https", description="secret_key")
    fs_region: str = Field(default="ap-guangzhou", description="region")
    fs_secure: bool = Field(default=False, description="secure")
    fs_connect_timeout: int = Field(default=3, description="连接超时时间")
    fs_read_timeout: int = Field(default=300, description="读超时")
    fs_write_timeout: int = Field(default=300, description="写超时")
    fs_retry_num: int = Field(default=5, description="重试次数，默认5次")

    @model_validator(mode="after")
    def after_validate(self):
        if not self.fs_secret_id:
            raise ValueError(f" {env_prefix}_secret_id is not found")
        return self


def get_interface_client(c: FileStorageConfig) -> ObjectInterface:
    if c.fs_type == FileStorageType.COS.value:
        from ._cos import CosImpl
        return CosImpl(c)

    elif c.fs_type == FileStorageType.Minio.value:
        from ._minio import MinioImpl
        return MinioImpl(c)

    elif c.fs_type == FileStorageType.OSS.value:
        from ._oss import OssImpl
        return OssImpl(c)
    else:
        raise TypeError(f"Unsupported file storage type: {c.type}")


def object_upload(obj: ObjectInterface,
                  file_path_name: str,
                  bytes_io: io.BytesIO,
                  length: Optional[int],
                  metadata=None,
                  **kwargs):
    return obj.upload(file_path_name, bytes_io, length, metadata, **kwargs)


def object_download(obj: ObjectInterface, file_path_name: str):
    return obj.download(file_path_name)


def object_exists(obj: ObjectInterface, file_path_name: str) -> Optional[Any]:
    return obj.object_exists(file_path_name)
