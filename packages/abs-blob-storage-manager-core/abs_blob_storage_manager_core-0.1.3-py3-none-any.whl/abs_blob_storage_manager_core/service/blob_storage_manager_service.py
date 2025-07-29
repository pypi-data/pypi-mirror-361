from typing import Any, List, Optional, Dict
from datetime import timedelta

from fastapi import UploadFile

from abs_blob_storage_manager_core.schema.blob_storage_schema import (
    BlobStorage,
    BlobStorageResponse,
    FileType,
    MultipleBlobStorageResponse,
    RequestData,
    CreateFolderRequest,
)
from abs_exception_core.exceptions import ValidationError
from abs_blob_storage_manager_core.repository.blob_storage_manager_repository import BlobStorageRepository
from abs_nosql_repository_core.service import BaseService
from abs_utils.logger import setup_logger


logger = setup_logger(__name__)


class BlobStorageManagerService(BaseService):
    SUPPORTED_CONTENT_TYPES = [
        # Documents
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        # Images
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        # Videos
        "video/mp4",
        "video/quicktime",
        "video/x-msvideo",
        # Audio
        "audio/mpeg",
        "audio/wav",
        "audio/ogg",
        # Archives
        "application/zip",
        "application/x-rar-compressed",
        "application/x-7z-compressed",
    ]
    
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

    def __init__(self, blob_storage_repository: BlobStorageRepository):
        super().__init__(blob_storage_repository)

    def _validate_file(self, file: UploadFile) -> None:
        """
        Validate a single file for upload.
        
        Args:
            file: The file to validate
            
        Raises:
            ValidationError: If validation fails
        """
        if not file:
            raise ValidationError(detail="No file provided")

        try:
            file.file.seek(0, 2)
            size = file.file.tell()
            file.file.seek(0)

            if size > self.MAX_FILE_SIZE:
                raise ValidationError(
                    detail=f"File size exceeds maximum limit of {self.MAX_FILE_SIZE/1024/1024}MB"
                )

            content_type = file.content_type
            if not content_type:
                raise ValidationError(detail="File content type not detected")

            if content_type not in self.SUPPORTED_CONTENT_TYPES:
                raise ValidationError(
                    detail=f"Unsupported file type: {content_type}. Supported types: {', '.join(self.SUPPORTED_CONTENT_TYPES)}"
                )

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(detail=f"Error validating file: {str(e)}")

    async def upload_file(
        self,
        file: UploadFile,
        request_data: Any,
        user_id: Optional[str] = None,
    ) -> BlobStorage:
        """
        Upload a single file to blob storage with validation.
        
        Args:
            file: The file to upload
            request_data: Upload configuration data
            user_id: ID of the user uploading the file
            
        Returns:
            BlobStorage: The created database record
            
        Raises:
            ValidationError: If file validation fails
        """
        self._validate_file(file)

        return await self.repository.upload_file(
            file=file, user_id=user_id, request_data=request_data
        )

    async def get_file_url(
        self,
        file_id: str,
        user_id: str,
        token_expiry: timedelta = timedelta(hours=1, minutes=0, seconds=0)
    ) -> str:
        """Get the URL for a file."""
        return await self.repository.get_file_url(file_id, user_id, token_expiry)

    async def get_file(self, file_id: str, user_id: str) -> tuple[BlobStorage, Any]:
        """Get a file by ID with streaming download."""
        return await self.repository.get_file(file_id, user_id)

    async def get_file_chunked(
        self,
        file_id: str,
        user_id: str,
        chunk_size: int = 8192,
        start_byte: Optional[int] = None,
        end_byte: Optional[int] = None,
    ) -> tuple[BlobStorage, Any]:
        """Get a file by ID with chunked streaming download for large files."""
        return await self.repository.get_file_chunked(
            file_id, user_id, chunk_size, start_byte, end_byte
        )

    async def get_file_in_memory(
        self, file_id: str, user_id: str, max_size_mb: int = 10
    ) -> tuple[BlobStorage, bytes]:
        """Get a file by ID, loading it into memory only if it's smaller than the specified limit."""
        return await self.repository.get_file_in_memory(file_id, user_id, max_size_mb)

    async def delete_file(self, file_id: str, user_id: str) -> None:
        """Delete a file."""
        await self.repository.delete_file(file_id, user_id)

    async def get_file_details(
        self,
        file_id: str,
        user_id: str,
        token_expiry: timedelta = timedelta(hours=1, minutes=0, seconds=0)
    ) -> BlobStorageResponse:
        """Get file details including URL by file ID."""
        return await self.repository.get_file_details(file_id, user_id, token_expiry)

    async def get_files_by_type(self, file_type: FileType, user_id: str) -> List[BlobStorage]:
        """Get files by type for a specific user."""
        return await self.repository.get_files_by_type(file_type, user_id)

    async def get_all_files(self, user_id: str) -> List[BlobStorage]:
        """Get all files for a specific user."""
        return await self.repository.get_all_files(user_id)

    async def get_public_files(self, user_id: str) -> List[BlobStorage]:
        """Get all public files for a specific user."""
        return await self.repository.get_public_files(user_id)

    async def cleanup_expired_files(self, user_id: str) -> int:
        """Clean up expired files for a specific user."""
        expired_files = await self.repository.get_expired_files(user_id)
        count = 0
        for file in expired_files:
            try:
                await self.delete_file(file["uuid"], user_id)
                count += 1
            except Exception as e:
                logger.error(f"Error deleting expired file {file['uuid']}: {str(e)}")
        return count

    async def upload_multiple_files(
        self,
        files: List[UploadFile],
        request_data: RequestData,
        current_user: Optional[str] = None,
        max_concurrency: Optional[int] = None,
    ) -> MultipleBlobStorageResponse:
        """
        Upload multiple files to blob storage with validation and concurrent processing.
        
        Args:
            files: List of files to upload
            request_data: Upload configuration data
            current_user: ID of the user uploading files
            max_concurrency: Maximum number of concurrent uploads (default: unlimited)
            
        Returns:
            MultipleBlobStorageResponse: Upload results with success/failure details
        """
        if not files:
            raise ValidationError(detail="No files provided")

        failed_files = []
        valid_files = []

        for file in files:
            try:
                self._validate_file(file)
                valid_files.append(file)
            except ValidationError as e:
                failed_files.append(
                    {
                        "filename": file.filename,
                        "error": str(e.detail),
                    }
                )
            except Exception as e:
                logger.error(f"Error validating file {file.filename}: {str(e)}")
                failed_files.append({"filename": file.filename, "error": str(e)})

        if not valid_files:
            return MultipleBlobStorageResponse(
                files=[],
                total_files=len(files),
                total_size=0,
                success_count=0,
                failed_count=len(files),
                failed_files=failed_files,
            )

        expires_at = request_data.expires_at
        metadata = request_data.file_metadata
        is_public = request_data.is_public
        container_name = request_data.container_name
        storage_path = request_data.storage_path

        if container_name is None and is_public:
            container_name = self.repository._public_container
        elif container_name is None and not is_public:
            container_name = self.repository._private_container

        try:
            uploaded_files = await self.repository.upload_multiple_files(
                files=valid_files,
                user_id=current_user,
                expires_at=expires_at,
                metadata=metadata,
                is_public=is_public,
                container_name=container_name,
                storage_path=storage_path,
                max_concurrency=max_concurrency,
            )

            total_size = sum(file["file_size"] for file in uploaded_files)

            return MultipleBlobStorageResponse(
                files=uploaded_files,
                total_files=len(files),
                total_size=total_size,
                success_count=len(uploaded_files),
                failed_count=len(failed_files),
                failed_files=failed_files,
            )

        except Exception as e:
            logger.error(f"Error in bulk upload: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

            return MultipleBlobStorageResponse(
                files=[],
                total_files=len(files),
                total_size=0,
                success_count=0,
                failed_count=len(files),
                failed_files=[
                    {"filename": file.filename, "error": str(e)} for file in files
                ],
            )

    async def create_folder(
        self,
        request_data: CreateFolderRequest,
        user_id: str,
    ) -> BlobStorage:
        """Create a folder in blob storage."""
        if not request_data.folder_name or "/" in request_data.folder_name:
            raise ValidationError(detail="Invalid folder name")

        folder_path = f"{request_data.parent_path}/{request_data.folder_name}" if request_data.parent_path else request_data.folder_name
        folder_path = folder_path.strip("/")

        return await self.repository.create_folder(
            request_data=request_data,
            user_id=user_id,
        )

    async def list_folder_contents(
        self,
        folder_path: str,
        user_id: str,
        is_public: bool = True,
        container_name: Optional[str] = None,
    ) -> List[BlobStorage]:
        """List contents of a folder."""
        try:
            import urllib.parse
            decoded_path = urllib.parse.unquote(folder_path)

            if decoded_path.endswith('/'):
                decoded_path = decoded_path[:-1]

            contents = await self.repository.list_folder_contents(
                folder_path=decoded_path,
                user_id=user_id,
                is_public=is_public,
                container_name=container_name,
            )

            return contents

        except Exception as e:
            logger.error(f"Service: Error in list_folder_contents: {str(e)}")
            logger.error(f"Service: Error type: {type(e)}")
            import traceback
            logger.error(f"Service: Traceback: {traceback.format_exc()}")
            raise

    async def delete_folder(
        self,
        folder_path: str,
        user_id: str,
        is_public: bool = True,
        container_name: Optional[str] = None,
    ) -> None:
        """Delete a folder and its contents."""
        if not folder_path:
            raise ValidationError(detail="Invalid folder path")

        await self.repository.delete_folder(
            folder_path=folder_path,
            user_id=user_id,
            is_public=is_public,
            container_name=container_name,
        )

    async def update_metadata(
            self,
            file_id: str,
            user_id: str,
            new_metadata: Dict[str, Any],
        ) -> BlobStorage:
            """
            Update metadata for a file or folder in both blob storage and the database.
            """
            await self.repository.update_metadata(
                file_id=file_id,
                user_id=user_id,
                new_metadata=new_metadata,
            )
