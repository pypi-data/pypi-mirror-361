import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import uuid
import asyncio
import time

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import (
    BlobSasPermissions,
    BlobServiceClient,
    ContainerClient,
    generate_blob_sas,
)
from fastapi import HTTPException, UploadFile
from abs_exception_core.exceptions import ValidationError

from abs_nosql_repository_core.repository import BaseRepository
from abs_blob_storage_manager_core.schema.blob_storage_schema import (
    BlobStorage,
    BlobStorageCreate,
    BlobStorageResponse,
    FileType,
    RequestData,
    CreateFolderRequest,
)
from abs_blob_storage_manager_core.schema.blob_storage_model import BlobStorageDocument
from abs_nosql_repository_core.schema.base_schema import FilterSchema, ListFilter, LogicalOperator, FieldOperatorCondition, Operator
from beanie import PydanticObjectId
from abs_exception_core.exceptions import NotFoundError, ValidationError, InternalServerError, PermissionDeniedError
from abs_utils.logger import setup_logger

logger = setup_logger(__name__)

class BlobStorageRepository(BaseRepository):
    def __init__(
        self,
        connection_string: str,
        public_container: str,
        private_container: str
    ):
        super().__init__(BlobStorageDocument)
        self._connection_string = connection_string
        self._public_container = public_container
        self._private_container = private_container

        if not connection_string:
            raise ValidationError(
                detail="Azure Storage connection string is not properly configured"
            )
        
        if not public_container or not private_container:
            raise ValidationError(
                detail="Public and private containers are not properly configured"
            )

        self._blob_service_client = BlobServiceClient.from_connection_string(
            self._connection_string
        )

        try:
            if self._public_container:
                self._blob_service_client.create_container(
                    self._public_container, public_access="container"
                )

        except ResourceExistsError:
            container_client = self._blob_service_client.get_container_client(
                self._public_container
            )
            container_client.set_container_access_policy(
                public_access="container",
                signed_identifiers={},
            )

        try:
            if self._private_container:
                self._blob_service_client.create_container(
                    self._private_container, public_access=None
                )
        except ResourceExistsError:
            container_client = self._blob_service_client.get_container_client(
                self._private_container
            )
            container_client.set_container_access_policy(
                public_access=None,
                signed_identifiers={},
            )

        self._allowed_extensions = {
            FileType.DOCUMENT: {".pdf", ".doc", ".docx", ".txt", ".rtf"},
            FileType.IMAGE: {".jpg", ".jpeg", ".png", ".gif", ".webp"},
            FileType.VIDEO: {".mp4", ".avi", ".mov", ".wmv"},
            FileType.AUDIO: {".mp3", ".wav", ".ogg", ".m4a"},
            FileType.ARCHIVE: {".zip", ".rar", ".7z", ".tar", ".gz"},
        }

    def _get_default_container_name(self, is_public: bool) -> str:
        """
        Get the default container name based on visibility.

        Args:
            is_public: Whether the container should be public

        Returns:
            str: The default container name
        """
        return self._public_container if is_public else self._private_container

    def _create_or_configure_container(
        self, 
        container_client: ContainerClient, 
        container_name: str, 
        is_public: bool
    ) -> ContainerClient:
        """
        Create container if it doesn't exist or configure its access policy.

        Args:
            container_client: The container client
            container_name: Name of the container
            is_public: Whether the container should be public

        Returns:
            ContainerClient: The configured container client
        """
        public_access = "container" if is_public else None
        
        if not container_client.exists():
            container_client = self._blob_service_client.create_container(
                container_name, public_access=public_access
            )
        else:
            container_client.set_container_access_policy(
                public_access=public_access,
                signed_identifiers={},
            )
        return container_client

    def _get_container_client(
        self, container_name: str, is_public: bool = True
    ) -> ContainerClient:
        """Get the appropriate container client for the specified container."""
        try:
            container_client = self._blob_service_client.get_container_client(container_name)
            return self._create_or_configure_container(container_client, container_name, is_public)

        except Exception as e:
            raise InternalServerError(detail=str(e))

    def _get_file_type(self, filename: str) -> FileType:
        """
        Determine file type based on extension.

        Args:
            filename: Name of the file

        Returns:
            FileType: The determined file type (document, image, video, etc.)
        """
        ext = os.path.splitext(filename)[1].lower()
        for file_type, extensions in self._allowed_extensions.items():
            if ext in extensions:
                return file_type
        return FileType.OTHER

    def _get_mime_type(self, filename: str) -> str:
        """
        Get MIME type based on file extension.

        Args:
            filename: Name of the file

        Returns:
            str: The MIME type for the file
        """
        ext = os.path.splitext(filename)[1].lower()
        mime_types = {
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".txt": "text/plain",
            ".rtf": "application/rtf",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".mp4": "video/mp4",
            ".avi": "video/x-msvideo",
            ".mov": "video/quicktime",
            ".wmv": "video/x-ms-wmv",
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".ogg": "audio/ogg",
            ".m4a": "audio/mp4",
            ".zip": "application/zip",
            ".rar": "application/x-rar-compressed",
            ".7z": "application/x-7z-compressed",
            ".tar": "application/x-tar",
            ".gz": "application/gzip",
        }
        return mime_types.get(ext, "application/octet-stream")

    def _get_blob_path(self, filename: str) -> str:
        """
        Generate a unique blob path for the file.

        Args:
            filename: Original filename

        Returns:
            str: A unique path for the blob including timestamp
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        return unique_filename

    def _generate_sas_url(
        self,
        blob_client,
        is_public: bool,
        token_expiry: timedelta = timedelta(hours=1, minutes=0, seconds=0)
    ) -> str:
        """
        Generate a SAS URL for private files or return direct URL for public files.

        Args:
            blob_client: The Azure blob client
            is_public: Whether the file is public

        Returns:
            str: The URL to access the file (direct for public, SAS for private)
        """
        if is_public:
            return blob_client.url

        sas_token = generate_blob_sas(
            account_name=blob_client.account_name,
            container_name=blob_client.container_name,
            blob_name=blob_client.blob_name,
            account_key=self._blob_service_client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + token_expiry,
        )
        return f"{blob_client.url}?{sas_token}"

    def _get_user_folder_path(self, user_id: str) -> str:
        """
        Get the user's folder path.

        Args:
            user_id: ID of the user

        Returns:
            str: The user's folder path
        """
        return f"{user_id}"

    def _get_folder_path(self, user_id: str, folder_path: str = "") -> str:
        """
        Get the full folder path including user folder.

        Args:
            user_id: ID of the user
            folder_path: Optional subfolder path

        Returns:
            str: The complete folder path
        """
        user_folder = self._get_user_folder_path(user_id)
        if folder_path:
            return f"{user_folder}/{folder_path.strip('/')}"
        return user_folder

    def _ensure_user_folder_exists(self, container_client: ContainerClient, user_id: str, is_public: bool, container_name: str) -> None:
        """Ensure user folder exists in the container."""
        user_folder_path = self._get_user_folder_path(user_id)
        user_folder_client = container_client.get_blob_client(f"{user_folder_path}/.folder")
        
        if not user_folder_client.exists():
            user_folder_client.upload_blob(b"", overwrite=True)
            user_folder_client.set_blob_metadata({
                "file_name": user_id,
                "file_type": "folder",
                "mime_type": "application/x-directory",
                "file_size": "0",
                "owner_id": user_id,
                "is_public": str(is_public),
                "container_name": container_name,
                "is_folder": "true",
            })


    async def _ensure_folder_path_exists(
        self,
        container_client: ContainerClient,
        user_id: str,
        storage_path: str,
        is_public: bool,
        container_name: str,
    ) -> None:
        """Ensure all folders in the path exist in both storage and database."""
        path_parts = storage_path.strip('/').split('/')
        current_path = ""

        for part in path_parts:
            current_path = f"{current_path}/{part}" if current_path else part
            full_folder_path = self._get_folder_path(user_id, current_path) if not is_public else current_path
            folder_marker_path = f"{full_folder_path}/.folder"
            folder_client = container_client.get_blob_client(folder_marker_path)

            if not folder_client.exists():
                folder_client.upload_blob(b"", overwrite=True)
                folder_client.set_blob_metadata({
                    "file_name": part,
                    "file_type": "folder",
                    "mime_type": "application/x-directory",
                    "file_size": "0",
                    "owner_id": user_id,
                    "is_public": str(is_public),
                    "container_name": container_name,
                    "is_folder": "true",
                })

            if full_folder_path != str(user_id):
                find_query = FilterSchema(
                    operator=LogicalOperator.AND,
                    conditions=[
                        FieldOperatorCondition(
                            field="storage_path",
                            operator=Operator.EQ,
                            value=full_folder_path
                        ),
                        FieldOperatorCondition(
                            field="owner_id",
                            operator=Operator.EQ,
                            value=user_id
                        ),
                        FieldOperatorCondition(
                            field="is_public",
                            operator=Operator.EQ,
                            value=str(is_public)
                        )
                    ]
                )
                db_records = await self.get_all(find=ListFilter(filters=find_query))
                
                if not db_records["founds"]:
                    await self._create_blob_storage_record(
                        file_name=part,
                        file_type=FileType.FOLDER,
                        mime_type="application/x-directory",
                        file_size=0,
                        storage_path=f"{full_folder_path}/",
                        user_id=user_id,
                        is_public=is_public,
                        container_name=container_name,
                        metadata=None,
                        is_folder=True,
                    )

    async def get_by_id(self, id: str, user_id: str, is_safe: bool = False) -> Optional[BlobStorage]:
        """
        Get a file by ID, ensuring user has access.

        Args:
            id: UUID of the file
            user_id: ID of the requesting user

        Returns:
            Optional[BlobStorage]: The file record if found and accessible

        Raises:
            PermissionDeniedError: If access is denied
        """
        file = await self.get_by_attr("id", id)

        if file and (int(file.get("owner_id")) != int(user_id)) and (not file.get("is_public") or not is_safe):
            raise PermissionDeniedError()
        return file

    async def _create_blob_storage_record(
        self,
        file_name: str,
        file_type: FileType,
        mime_type: str,
        file_size: int,
        storage_path: str,
        user_id: str,
        is_public: bool,
        container_name: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict] = None,
        is_folder: bool = False,
    ) -> BlobStorage:
        """
        Create a BlobStorage record in the database.

        Args:
            file_name: Name of the file or folder
            file_type: Type of the file (document, image, etc.)
            mime_type: MIME type of the file
            file_size: Size of the file in bytes
            storage_path: Full path in storage
            user_id: ID of the owner
            is_public: Whether the file is public
            container_name: Optional custom container name
            expires_at: Optional expiration date
            metadata: Optional additional metadata
            is_folder: Whether this is a folder

        Returns:
            BlobStorage: The created database record
        """
        if container_name is None:
            container_name = self._public_container if is_public else self._private_container

        blob_data = BlobStorageCreate(
            file_name=file_name,
            file_type=file_type,
            mime_type=mime_type,
            file_size=file_size,
            storage_path=storage_path,
            expires_at=expires_at,
            owner_id=user_id,
            is_public=is_public,
            container_name=container_name,
            file_metadata=metadata or {},
            is_folder=is_folder,
        )
        return await self.create(blob_data)

    def _set_blob_metadata(
        self,
        blob_client: Any,
        file_name: str,
        file_type: str,
        mime_type: str,
        file_size: int,
        user_id: str,
        is_public: bool,
        container_name: str,
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict] = None,
        is_folder: bool = False,
    ) -> None:
        """
        Set metadata for a blob in Azure Storage.

        Args:
            blob_client: The Azure blob client
            file_name: Name of the file
            file_type: Type of the file
            mime_type: MIME type of the file
            file_size: Size of the file in bytes
            user_id: ID of the owner
            is_public: Whether the file is public
            container_name: Name of the container
            expires_at: Optional expiration date
            metadata: Optional additional metadata
            is_folder: Whether this is a folder
        """
        blob_metadata = {
            "file_name": file_name,
            "file_type": file_type,
            "mime_type": mime_type,
            "file_size": str(file_size),
            "owner_id": user_id,
            "is_public": str(is_public),
            "container_name": container_name or "",
            "expires_at": expires_at.isoformat() if expires_at else None,
            "is_folder": str(is_folder).lower(),
        }
        if metadata:
            blob_metadata.update(metadata)
        blob_client.set_blob_metadata(blob_metadata)

    async def _ensure_folder_exists(
        self,
        container_client: ContainerClient,
        folder_path: str,
        user_id: str,
        is_public: bool,
        container_name: str,
        metadata: Optional[Dict] = None,
    ) -> None:
        """
        Ensure a folder exists in both storage and database.

        Args:
            container_client: The Azure container client
            folder_path: Path of the folder
            user_id: ID of the owner
            is_public: Whether the folder is public
            container_name: Name of the container
            metadata: Optional additional metadata

        Note:
            Creates the folder in both Azure Storage and the database if it doesn't exist
        """
        folder_marker_path = f"{folder_path}/.folder"
        folder_client = container_client.get_blob_client(folder_marker_path)

        if not folder_client.exists():
            folder_client.upload_blob(b"", overwrite=True)
            self._set_blob_metadata(
                blob_client=folder_client,
                file_name=os.path.basename(folder_path),
                file_type="folder",
                mime_type="application/x-directory",
                file_size=0,
                user_id=user_id,
                is_public=is_public,
                container_name=container_name,
                metadata=metadata,
                is_folder=True,
            )

            find_query = FilterSchema(
                operator=LogicalOperator.AND,
                conditions=[
                    FieldOperatorCondition(
                        field="storage_path",
                        operator=Operator.EQ,
                        value=folder_path
                    ),
                    FieldOperatorCondition(
                        field="owner_id",
                        operator=Operator.EQ,
                        value=user_id
                    ),
                    FieldOperatorCondition(
                        field="is_public",
                        operator=Operator.EQ,
                        value=str(is_public)
                    )
                ]
            )
            db_records = await self.get_all(find=ListFilter(filters=find_query))
            
            if not db_records["founds"] and folder_path != str(user_id):
                await self._create_blob_storage_record(
                    file_name=os.path.basename(folder_path),
                    file_type=FileType.FOLDER,
                    mime_type="application/x-directory",
                    file_size=0,
                    storage_path=f"{folder_path}/",
                    user_id=user_id,
                    is_public=is_public,
                    container_name=container_name,
                    metadata=metadata,
                    is_folder=True,
                )

    async def _delete_blob_and_record(
        self,
        blob_path: str,
        container_client: ContainerClient,
    ) -> None:
        """
        Delete a blob and its database record.

        Args:
            blob_path: Path of the blob in storage
            user_id: ID of the owner
            container_client: The Azure container client

        Note:
            Silently handles errors to allow bulk operations to continue
        """
        try:
            blob_client = container_client.get_blob_client(blob_path)
            if blob_client.exists():
                blob_client.delete_blob()

        except Exception as e:
            logger.error(f"Error deleting blob and record {blob_path}: {str(e)}")

    async def _prepare_upload_environment(
        self,
        user_id: Optional[str],
        is_public: bool,
        container_name: Optional[str],
        storage_path: Optional[str],
    ) -> tuple[ContainerClient, str, str]:
        """
        Prepare the upload environment by setting up container client and ensuring folders exist.

        Args:
            user_id: ID of the user uploading files
            is_public: Whether files should be public
            container_name: Optional custom container name
            storage_path: Optional folder path to upload to

        Returns:
            tuple[ContainerClient, str, str]: Container client, container name, and user folder path
        """
        if not container_name:
            container_name = self._get_default_container_name(is_public)
        
        container_client = self._get_container_client(container_name, is_public)

        user_folder_path = ""
        if not is_public:
            if not user_id:
                raise ValidationError(detail="User ID is required for private files")

            user_folder_path = self._get_user_folder_path(user_id)
            await self._ensure_folder_exists(
                container_client=container_client,
                folder_path=user_folder_path,
                user_id=user_id,
                is_public=is_public,
                container_name=container_name,
            )

        if storage_path:
            await self._ensure_folder_path_exists(
                container_client=container_client,
                user_id=user_id,
                storage_path=storage_path,
                is_public=is_public,
                container_name=container_name,
            )

        return container_client, container_name, user_folder_path

    async def _upload_single_file_to_storage(
        self,
        file: UploadFile,
        container_client: ContainerClient,
        user_id: Optional[str],
        is_public: bool,
        container_name: str,
        user_folder_path: str,
        storage_path: Optional[str],
        expires_at: Optional[datetime],
        metadata: Optional[Dict],
    ) -> tuple[BlobStorageCreate, str]:
        """
        Upload a single file to blob storage and prepare database record.
        
        Args:
            file: The file to upload
            container_client: The Azure container client
            user_id: ID of the user uploading the file
            is_public: Whether the file should be public
            container_name: Name of the container
            user_folder_path: User's folder path (empty for public files)
            storage_path: Optional folder path to upload to
            expires_at: Optional expiration date
            metadata: Optional metadata
            
        Returns:
            tuple[BlobStorageCreate, str]: Database record data and full blob path
        """
        content = await file.read()
        file_type = self._get_file_type(file.filename)
        mime_type = self._get_mime_type(file.filename)
        blob_path = self._get_blob_path(file.filename)
        
        if is_public:
            full_blob_path = f"{storage_path}/{blob_path}" if storage_path else blob_path
        else:
            full_blob_path = f"{user_folder_path}/{storage_path}/{blob_path}" if storage_path else f"{user_folder_path}/{blob_path}"

        blob_client = container_client.get_blob_client(full_blob_path)
        blob_client.upload_blob(content, overwrite=True)

        self._set_blob_metadata(
            blob_client=blob_client,
            file_name=file.filename,
            file_type=file_type,
            mime_type=mime_type,
            file_size=len(content),
            user_id=user_id,
            is_public=is_public,
            container_name=container_name,
            expires_at=expires_at,
            metadata=metadata,
        )

        file_data = BlobStorageCreate(
            file_name=file.filename,
            file_type=file_type,
            mime_type=mime_type,
            file_size=len(content),
            storage_path=full_blob_path,
            expires_at=expires_at,
            owner_id=user_id,
            is_public=is_public,
            container_name=container_name,
            file_metadata=metadata or {},
        )
        
        return file_data, full_blob_path

    async def upload_file(
        self,
        file: UploadFile,
        request_data: RequestData,
        user_id: Optional[str] = None,
    ) -> BlobStorage:
        """
        Upload a single file to blob storage and database.

        Args:
            file: The file to upload
            user_id: ID of the user uploading the file
            request_data: JSON string containing upload parameters:
                - expires_at: Optional expiration date
                - file_metadata: Optional metadata
                - is_public: Whether the file should be public
                - container_name: Optional custom container name
                - storage_path: Optional folder path to upload to

        Returns:
            BlobStorage: The created database record

        Raises:
            HTTPException: If there's an error during upload
        """
        container_client, container_name, user_folder_path = await self._prepare_upload_environment(
            user_id, request_data.is_public, request_data.container_name, request_data.storage_path
        )

        file_data, full_blob_path = await self._upload_single_file_to_storage(
            file,
            container_client,
            user_id,
            request_data.is_public,
            container_name,
            user_folder_path,
            request_data.storage_path,
            request_data.expires_at,
            request_data.file_metadata,
        )

        return await self.create(file_data)

    async def get_file_url(
        self,
        file_id: str,
        user_id: str,
        token_expiry: timedelta = timedelta(hours=1, minutes=0, seconds=0)
    ) -> str:
        """
        Get the URL for a file.

        Args:
            file_id: UUID of the file
            user_id: ID of the requesting user

        Returns:
            str: The URL to access the file

        Raises:
            NotFoundError: If the file doesn't exist
        """
        blob = await self.get_by_id(file_id, user_id, is_safe=True)
        if not blob:
            raise NotFoundError(detail=f"File with ID {file_id} not found")

        container_client = self._get_container_client(
            blob["container_name"], blob["is_public"]
        )

        blob_client = container_client.get_blob_client(blob["storage_path"])
        if not blob_client.exists():
            raise NotFoundError(detail=f"File {blob['storage_path']} not found in storage")

        return self._generate_sas_url(blob_client, blob["is_public"], token_expiry)

    async def get_file(self, file_id: str, user_id: str) -> tuple[BlobStorage, Any]:
        """
        Get a file by ID with streaming download.

        Args:
            file_id: UUID of the file
            user_id: ID of the requesting user

        Returns:
            tuple[BlobStorage, Any]: The file record and a streaming download object

        Raises:
            NotFoundError: If the file doesn't exist
        """
        blob = await self.get_by_id(file_id, user_id, is_safe=True)
        if not blob:
            raise NotFoundError(detail=f"File with ID {file_id} not found")

        container_client = self._get_container_client(
            blob["container_name"], blob["is_public"]
        )

        blob_client = container_client.get_blob_client(blob["storage_path"])
        if not blob_client.exists():
            raise NotFoundError(detail=f"File {blob['storage_path']} not found in storage")

        download_stream = blob_client.download_blob()
        return blob, download_stream

    async def get_file_chunked(
        self,
        file_id: str,
        user_id: str,
        chunk_size: int = 8192,
        start_byte: Optional[int] = None,
        end_byte: Optional[int] = None,
    ) -> tuple[BlobStorage, Any]:
        """
        Get a file by ID with chunked streaming download for large files.

        Args:
            file_id: UUID of the file
            user_id: ID of the requesting user
            chunk_size: Size of chunks to read (default: 8KB)
            start_byte: Optional start byte for range requests
            end_byte: Optional end byte for range requests

        Returns:
            tuple[BlobStorage, Any]: The file record and a chunked streaming download object

        Raises:
            NotFoundError: If the file doesn't exist
        """
        blob = await self.get_by_id(file_id, user_id, is_safe=True)
        if not blob:
            raise NotFoundError(detail=f"File with ID {file_id} not found")

        container_client = self._get_container_client(
            blob["container_name"], blob["is_public"]
        )

        blob_client = container_client.get_blob_client(blob["storage_path"])
        if not blob_client.exists():
            raise NotFoundError(detail=f"File {blob['storage_path']} not found in storage")

        if start_byte is not None or end_byte is not None:
            download_stream = blob_client.download_blob(
                start=start_byte,
                length=end_byte - start_byte + 1 if end_byte else None
            )
        else:
            download_stream = blob_client.download_blob()

        return blob, download_stream

    async def get_file_in_memory(self, file_id: str, user_id: str, max_size_mb: int = 10) -> tuple[BlobStorage, bytes]:
        """
        Get a file by ID, loading it into memory only if it's smaller than the specified limit.

        Args:
            file_id: UUID of the file
            user_id: ID of the requesting user
            max_size_mb: Maximum file size in MB to load into memory (default: 10MB)

        Returns:
            tuple[BlobStorage, bytes]: The file record and its contents (if small enough)

        Raises:
            NotFoundError: If the file doesn't exist
            ValidationError: If the file is too large to load into memory
        """
        blob = await self.get_by_id(file_id, user_id, is_safe=True)
        if not blob:
            raise NotFoundError(detail=f"File with ID {file_id} not found")

        max_size_bytes = max_size_mb * 1024 * 1024
        if blob["file_size"] > max_size_bytes:
            raise ValidationError(
                detail=f"File size ({blob['file_size']} bytes) exceeds memory limit ({max_size_bytes} bytes). "
                       f"Use get_file() for streaming download instead."
            )

        container_client = self._get_container_client(
            blob["container_name"], blob["is_public"]
        )

        blob_client = container_client.get_blob_client(blob["storage_path"])
        if not blob_client.exists():
            raise NotFoundError(detail=f"File {blob['storage_path']} not found in storage")

        download_stream = blob_client.download_blob()
        return blob, download_stream.readall()

    async def delete_file(self, file_id: str, user_id: str) -> None:
        """
        Delete a file or folder.
        """
        blob = await self.get_by_id(file_id, user_id)
        if not blob:
            raise NotFoundError(detail=f"File with ID {file_id} not found")

        container_client = self._get_container_client(
            blob["container_name"], blob["is_public"]
        )

        blob_client = container_client.get_blob_client(blob["storage_path"])
        if not blob.get("is_folder", False):
            if blob_client.exists():
                blob_client.delete_blob()
        else:
            if blob_client.exists():
                blob_client.delete_blob()

        await self.delete(blob["id"])

    async def get_file_details(
        self,
        file_id: str,
        user_id: str,
        token_expiry: timedelta = timedelta(hours=1, minutes=0, seconds=0)
    ) -> BlobStorageResponse:
        """
        Get file details including URL by file ID.

        Args:
            file_id: UUID of the file
            user_id: ID of the requesting user

        Returns:
            BlobStorageResponse: Detailed file information including URL

        Raises:
            NotFoundError: If the file doesn't exist
        """
        blob = await self.get_by_id(file_id, user_id, is_safe=True)
        if not blob:
            raise NotFoundError(detail=f"File with ID {file_id} not found")

        container_client = self._get_container_client(
            blob["container_name"], blob["is_public"]
        )

        blob_client = container_client.get_blob_client(blob["storage_path"])
        if not blob_client.exists():
            raise NotFoundError(detail=f"File {blob['storage_path']} not found in storage")

        blob_properties = blob_client.get_blob_properties()

        url = self._generate_sas_url(blob_client, blob["is_public"], token_expiry)

        return BlobStorageResponse(
            id=blob["uuid"],
            file_name=blob["file_name"],
            file_type=blob["file_type"],
            mime_type=blob["mime_type"],
            file_size=blob["file_size"],
            storage_path=blob["storage_path"],
            expires_at=blob["expires_at"],
            owner_id=blob["owner_id"],
            is_public=blob["is_public"],
            container_name=blob["container_name"],
            file_metadata=blob["file_metadata"],
            url=url,
            created_at=blob["created_at"],
            updated_at=blob["updated_at"],
            last_modified=blob_properties.last_modified,
            etag=blob_properties.etag,
            content_length=blob_properties.size,
            content_type=blob_properties.content_settings.content_type,
        )

    async def get_files_by_type(self, file_type: FileType, user_id: str) -> List[BlobStorage]:
        """
        Get files by type for a specific user.

        Args:
            file_type: Type of files to retrieve
            user_id: ID of the user

        Returns:
            List[BlobStorage]: List of files of the specified type
        """
        find_query = FilterSchema(
                operator="and",
                conditions=[
                {"field": "file_type", "operator": "eq", "value": file_type},
                {"field": "owner_id", "operator": "eq", "value": user_id}
                ]
            )
        query = await self.get_all(find=ListFilter(filters=find_query))
        return query["founds"]

    async def get_all_files(self, user_id: str) -> List[BlobStorage]:
        """
        Get all files for a specific user.

        Args:
            user_id: ID of the user

        Returns:
            List[BlobStorage]: List of all user's files
        """
        find_query = FilterSchema(
            operator="and",
            conditions=[
                {"field": "owner_id", "operator": "eq", "value": user_id},
                {"field": "file_type", "operator": "ne", "value": "folder"}
            ]
        )
        query = await self.get_all(find=ListFilter(filters=find_query))
        return query["founds"]

    async def get_public_files(self, user_id: str) -> List[BlobStorage]:
        """
        Get all public files for a specific user.

        Args:
            user_id: ID of the user

        Returns:
            List[BlobStorage]: List of user's public files
        """
        find_query = FilterSchema(
                operator="and",
                conditions=[
                    {"field": "is_public", "operator": "eq", "value": True},
                    {"field": "owner_id", "operator": "eq", "value": user_id},
                    {"field": "file_type", "operator": "ne", "value": "folder"}
                ]
            )
        query = await self.get_all(find=ListFilter(filters=find_query))
        return query["founds"]

    async def get_expired_files(self, user_id: str) -> List[BlobStorage]:
        """
        Get all expired files for a specific user.

        Args:
            user_id: ID of the user

        Returns:
            List[BlobStorage]: List of user's expired files
        """
        find_query = FilterSchema(
                operator="and",
                conditions=[
                {"field": "expires_at", "operator": "lt", "value": datetime.utcnow()},
                {"field": "owner_id", "operator": "eq", "value": user_id}
                ]
            )
        query = await self.get_all(find=ListFilter(filters=find_query))
        return query["founds"]

    async def upload_multiple_files(
        self,
        files: List[UploadFile],
        user_id: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict] = None,
        is_public: bool = True,
        container_name: Optional[str] = None,
        storage_path: Optional[str] = None,
        max_concurrency: Optional[int] = None,
    ) -> List[BlobStorage]:
        """
        Upload multiple files to blob storage and database concurrently.

        Args:
            files: List of files to upload
            user_id: ID of the user uploading files
            expires_at: Optional expiration date for files
            metadata: Optional metadata to apply to all files
            is_public: Whether files should be public
            container_name: Optional custom container name
            storage_path: Optional folder path to upload files to
            max_concurrency: Maximum number of concurrent uploads (default: unlimited)

        Returns:
            List[BlobStorage]: List of created database records

        Raises:
            HTTPException: If there's an error during upload
        """
        try:
            container_client, container_name, user_folder_path = await self._prepare_upload_environment(
                user_id, is_public, container_name, storage_path
            )

            upload_coroutines = []
            for file in files:
                coro = self._upload_single_file_to_storage(
                    file,
                    container_client,
                    user_id,
                    is_public,
                    container_name,
                    user_folder_path,
                    storage_path,
                    expires_at,
                    metadata,
                )
                upload_coroutines.append(coro)

            if max_concurrency and max_concurrency > 0:
                semaphore = asyncio.Semaphore(max_concurrency)
                
                async def limited_upload(coro):
                    async with semaphore:
                        return await coro
                
                limited_coroutines = [limited_upload(coro) for coro in upload_coroutines]
                upload_results = await asyncio.gather(*limited_coroutines, return_exceptions=True)
            else:
                upload_results = await asyncio.gather(*upload_coroutines, return_exceptions=True)

            files_data = []
            for i, result in enumerate(upload_results):
                if isinstance(result, Exception):
                    logger.error(f"Error uploading file {files[i].filename}: {str(result)}")
                    continue
                
                file_data, _ = result
                files_data.append(file_data)

            if not files_data:
                raise ValidationError(detail="No files were successfully uploaded")

            return await self.bulk_create(files_data)

        except Exception as e:
            logger.error(f"Error during upload: {str(e)}")
            raise

    async def create_folder(
        self,
        request_data: CreateFolderRequest,
        user_id: str,
    ) -> BlobStorage:
        """
        Create a folder in blob storage.

        Args:
            folder_name: Name of the folder to create
            user_id: ID of the user creating the folder
            parent_path: Optional parent folder path
            is_public: Whether the folder should be public
            container_name: Optional custom container name
            metadata: Optional additional metadata

        Returns:
            BlobStorage: The created folder record

        Raises:
            ValidationError: If the folder name is invalid
        """
        if not request_data.folder_name or "/" in request_data.folder_name:
            raise ValidationError(detail="Invalid folder name")

        container_name = request_data.container_name
        if container_name is None:
            container_name = self._get_default_container_name(request_data.is_public)

        container_client = self._get_container_client(container_name, request_data.is_public)

        self._ensure_user_folder_exists(container_client, user_id, request_data.is_public, container_name)

        path = f"{request_data.parent_path}/{request_data.folder_name}" if request_data.parent_path else request_data.folder_name
        full_folder_path = self._get_folder_path(user_id, path) if not request_data.is_public else path
        folder_marker_path = f"{full_folder_path}/.folder"
        blob_client = container_client.get_blob_client(folder_marker_path)
        
        folder_metadata = {
            "file_name": request_data.folder_name,
            "file_type": "folder",
            "mime_type": "application/x-directory",
            "file_size": "0",
            "owner_id": user_id,
            "is_public": str(request_data.is_public),
            "container_name": container_name,
            "is_folder": "true",
        }
        if request_data.metadata:
            folder_metadata.update(request_data.metadata)

        try:
            blob_client.upload_blob(b"", overwrite=True)
            blob_client.set_blob_metadata(folder_metadata)
        except Exception as e:
            logger.error(f"Error creating folder marker at '{folder_marker_path}': {e}")
            raise

        folder_data = BlobStorageCreate(
            file_name=request_data.folder_name,
            file_type=FileType.FOLDER,
            mime_type="application/x-directory",
            file_size=0,
            storage_path=full_folder_path,
            owner_id=user_id,
            is_public=request_data.is_public,
            container_name=container_name,
            file_metadata=request_data.metadata or {},
            is_folder=True,
        )

        return await self.create(folder_data)

    async def list_folder_contents(
        self,
        folder_path: str,
        user_id: str,
        is_public: bool = True,
        container_name: Optional[str] = None,
    ) -> List[BlobStorage]:
        """
        List contents of a folder.

        Args:
            folder_path: Path of the folder to list
            user_id: ID of the requesting user
            is_public: Whether the folder is public
            container_name: Optional custom container name

        Returns:
            List[BlobStorage]: List of files and folders in the specified path

        Note:
            Returns both files and subfolders in the specified path
        """
        try:
            if container_name is None:
                container_name = self._get_default_container_name(is_public)
            
            container_client = self._get_container_client(container_name, is_public)

            self._ensure_user_folder_exists(container_client, user_id, is_public, container_name)

            full_folder_path = self._get_folder_path(user_id, folder_path) if not is_public else folder_path

            prefix = f"{full_folder_path}/" if full_folder_path else "" 

            blobs = container_client.list_blobs(name_starts_with=prefix)
            blob_list = list(blobs)

            folders = set()
            file_paths = []
            folder_contents = []

            for blob in blob_list:
                relative_path = blob.name[len(prefix):]
                if not relative_path:
                    continue

                parts = relative_path.split('/')
                if len(parts) > 1:
                    folder_name = parts[0]
                    folder_path = f"{full_folder_path}/{folder_name}"
                    folders.add(folder_path)

                elif not blob.name.endswith('/.folder'):
                    file_paths.append(blob.name)

            all_paths = file_paths + list(folders)

            if all_paths:
                find_query = FilterSchema(
                    operator=LogicalOperator.AND,
                    conditions=[
                        FieldOperatorCondition(
                            field="storage_path",
                            operator=Operator.IN,
                            value=all_paths
                        ),
                        FieldOperatorCondition(
                            field="owner_id",
                            operator=Operator.EQ,
                            value=user_id
                        ),
                        FieldOperatorCondition(
                            field="is_public",
                            operator=Operator.EQ,
                            value=is_public
                        )
                    ]
                )
                db_records = await self._get_all_paginated(find_query)
                
                db_lookup = {record["storage_path"]: record for record in db_records}

            else:
                db_lookup = {}

            missing_files = []
            for blob in blob_list:
                relative_path = blob.name[len(prefix):]
                if not relative_path:
                    continue

                parts = relative_path.split('/')
                if len(parts) > 1:
                    continue
                elif not blob.name.endswith('/.folder'):
                    if blob.name in db_lookup:
                        folder_contents.append(db_lookup[blob.name])
                    else:
                        missing_files.append(blob.name)

            if missing_files:
                missing_metadata = await self._batch_get_blob_metadata(container_client, missing_files)
                
                for blob_name, metadata in missing_metadata.items():
                    try:
                        blob_data = BlobStorage(
                            id=str(PydanticObjectId()),
                            file_name=metadata.get("file_name", os.path.basename(blob_name)),
                            file_type=metadata.get("file_type", "file"),
                            mime_type=metadata.get("mime_type", "application/octet-stream"),
                            file_size=int(metadata.get("file_size", "0")),
                            storage_path=blob_name,
                            owner_id=metadata.get("owner_id", user_id),
                            is_public=metadata.get("is_public", str(is_public)).lower() == "true",
                            container_name=metadata.get("container_name", container_name),
                            file_metadata=metadata,
                            is_folder=False,
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow(),
                        )
                        folder_contents.append(blob_data)
                    except Exception as e:
                        logger.error(f"Error processing blob {blob_name}: {str(e)}")
                        continue

            for folder_path in folders:
                if folder_path in db_lookup:
                    folder_contents.append(db_lookup[folder_path])

                else:
                    folder_name = os.path.basename(folder_path)
                    folder_data = BlobStorage(
                        id=str(PydanticObjectId()),
                        file_name=folder_name,
                        file_type="folder",
                        mime_type="folder",
                        file_size=0,
                        storage_path=folder_path,
                        owner_id=user_id,
                        is_public=is_public,
                        container_name=container_name,
                        file_metadata={},
                        is_folder=True,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )
                    folder_contents.append(folder_data)

            return folder_contents

        except Exception as e:
            logger.error(f"Error in list_folder_contents: {str(e)}")
            raise

    async def _get_all_paginated(
        self,
        find_query: FilterSchema,
        page_size: int = 100,
        timeout: int = 30,
        max_pages: int = 1000,
    ) -> List[Any]:
        """
        Helper method to get all records across multiple pages, with timeout and max page safeguards.

        Args:
            find_query: The filter query to use
            page_size: Number of records per page
            timeout: Maximum time in seconds to spend paginating
            max_pages: Maximum number of pages to fetch

        Returns:
            List[Any]: Combined list of all records across all pages
        """
        all_records = []
        current_page = 1
        start_time = time.monotonic()
        while current_page <= max_pages:
            if time.monotonic() - start_time > timeout:
                logger.warning(f"Pagination timeout after {timeout} seconds on page {current_page}")
                break
            try:
                result = await self.get_all(find=ListFilter(filters=find_query, page=current_page, page_size=page_size))
            except Exception as e:
                logger.error(f"Exception during pagination on page {current_page}: {e}")
                break
            if not result["founds"]:
                break
                
            all_records.extend(result["founds"])
            if len(result["founds"]) < page_size:
                break
                
            current_page += 1
            
        return all_records

    async def delete_folder_recursive(
        self,
        folder_path: str,
        user_id: str,
        is_public: bool = True,
        container_name: Optional[str] = None,
    ) -> bool:
        """Delete a folder and all its contents recursively."""
        try:
            if container_name is None:
                container_name = self._get_default_container_name(is_public)

            container_client = self._get_container_client(container_name, is_public)

            if is_public:
                full_folder_path = folder_path
            else:
                full_folder_path = self._get_folder_path(user_id, folder_path)
                stripped_path = full_folder_path.strip("/").split("/")
                full_folder_path = full_folder_path if len(stripped_path) > 1 else stripped_path[0]

            find_query = FilterSchema(
                operator=LogicalOperator.AND,
                conditions=[
                    FieldOperatorCondition(
                        field="storage_path",
                        operator=Operator.LIKE,
                        value=f"{full_folder_path}//*" if full_folder_path != "/" else "/*"
                    ),
                    FieldOperatorCondition(
                        field="owner_id",
                        operator=Operator.EQ,
                        value=user_id
                    ),
                    FieldOperatorCondition(
                        field="is_public",
                        operator=Operator.EQ,
                        value=is_public
                    )
                ]
            )

            db_records = await self._get_all_paginated(find_query)
            delete_coros = [self._delete_blob_and_record(blob["storage_path"] if not blob["is_folder"] else blob["storage_path"] + ".folder", container_client) for blob in db_records]
            await asyncio.gather(*delete_coros, return_exceptions=True)

            await self.bulk_delete(conditions=find_query)

            return True

        except Exception as e:
            logger.error(f"Error in delete_folder_recursive: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def delete_folder(
        self,
        folder_path: str,
        user_id: str,
        is_public: bool = True,
        container_name: Optional[str] = None,
    ) -> bool:
        """
        Delete a folder and all its contents.
        """
        try:
            await self.delete_folder_recursive(
                folder_path=folder_path,
                user_id=user_id,
                is_public=is_public,
                container_name=container_name,
            )

            return True

        except Exception as e:
            logger.error(f"Error in delete_folder: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def update_metadata(
        self,
        file_id: str,
        user_id: str,
        new_metadata: Dict[str, Any],
    ) -> BlobStorage:
        """
        Update metadata for a file or folder in both blob storage and the database.
        """
        blob = await self.get_by_id(file_id, user_id)
        if not blob:
            raise NotFoundError(detail=f"File with ID {file_id} not found")

        container_client = self._get_container_client(blob["container_name"], blob["is_public"])
        blob_client = container_client.get_blob_client(blob["storage_path"])
        current_metadata = blob_client.get_blob_properties().metadata
        updated_metadata = {**current_metadata, **new_metadata}
        blob_client.set_blob_metadata(updated_metadata)

        update_data = {"file_metadata": updated_metadata}
        await self.update(blob["id"], update_data)

        return await self.get_by_id(file_id, user_id)

    async def _batch_get_blob_metadata(self, container_client: ContainerClient, blob_names: List[str]) -> Dict[str, Dict]:
        """
        Batch retrieve metadata for multiple blobs concurrently.

        Args:
            container_client: The Azure container client
            blob_names: List of blob names

        Returns:
            Dict[str, Dict]: Dictionary of blob names and their metadata
        """
        async def get_single_blob_metadata(blob_name: str) -> tuple[str, Dict]:
            try:
                blob_client = container_client.get_blob_client(blob_name)
                metadata = blob_client.get_blob_properties().metadata
                return blob_name, metadata
            except Exception as e:
                logger.error(f"Error getting metadata for {blob_name}: {str(e)}")
                return blob_name, {}

        metadata_coroutines = [get_single_blob_metadata(blob_name) for blob_name in blob_names]
        results = await asyncio.gather(*metadata_coroutines, return_exceptions=True)
        
        metadata_dict = {}
        for result in results:
            if isinstance(result, Exception):
                continue
            blob_name, metadata = result
            metadata_dict[blob_name] = metadata
            
        return metadata_dict
