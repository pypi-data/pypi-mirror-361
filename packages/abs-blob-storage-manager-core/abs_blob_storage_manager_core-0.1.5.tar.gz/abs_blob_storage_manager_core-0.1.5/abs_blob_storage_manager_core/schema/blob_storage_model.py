from datetime import datetime
from typing import Optional
from abs_nosql_repository_core.document import BaseDocument
from pydantic import Field

from abs_blob_storage_manager_core.schema.blob_storage_schema import FileType


class BlobStorageDocument(BaseDocument):
    file_name: str = Field(..., description="The name of the file")
    file_type: FileType = Field(..., description="The type of the file")
    mime_type: str = Field(..., description="The mime type of the file")
    file_size: int = Field(..., description="The size of the file")
    storage_path: str = Field(..., description="The path of the file")
    file_metadata: dict = Field(..., description="The metadata of the file")
    is_public: bool = Field(True, description="Whether the file is public")
    expires_at: Optional[datetime] = Field(None, description="The expiration date of the file")
    owner_id: Optional[str] = Field(None, description="The id of the owner of the file")
    container_name: Optional[str] = Field(None, description="The name of the container")
    is_folder: bool = Field(False, description="Whether the file is a folder")

    class Settings:
        name = "blob_storage"
