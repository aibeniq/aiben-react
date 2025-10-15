import magic
import os
import re
import uuid
import zipfile
from pathlib import Path
from fastapi import UploadFile, HTTPException

ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.docx', '.xlsx', '.csv', '.doc'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
MAX_FILENAME_LENGTH = 255
MAX_ZIP_RATIO = 100  # Max compression ratio
MAX_ZIP_FILES = 10000  # Max files in ZIP

class FileValidator:
    @staticmethod
    def validate_upload(file: UploadFile) -> tuple[bool, str]:
        """Comprehensive file upload validation"""
        # 1. Validate filename
        if not file.filename or len(file.filename) > MAX_FILENAME_LENGTH:
            return False, "Invalid filename"
        # 2. Check for path traversal
        if '..' in file.filename or '/' in file.filename or '\\' in file.filename:
            return False, "Invalid filename characters"
        # 3. Validate extension
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            return False, f"File type {ext} not allowed"
        # 4. Validate MIME type (use python-magic)
        content = file.file.read(2048)  # Read first 2KB
        file.file.seek(0)  # Reset for later reading
        mime = magic.from_buffer(content, mime=True)
        expected_mimes = {
            '.pdf': ['application/pdf'],
            '.txt': ['text/plain'],
            '.docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
            '.xlsx': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
            '.csv': ['text/csv', 'text/plain'],
        }
        if mime not in expected_mimes.get(ext, []):
            return False, f"MIME type {mime} doesn't match extension {ext}"
        # 5. Check file size
        file.file.seek(0, 2)  # Seek to end
        size = file.file.tell()
        file.file.seek(0)  # Reset
        if size > MAX_FILE_SIZE:
            return False, f"File size {size} exceeds maximum {MAX_FILE_SIZE}"
        return True, "Valid"

    @staticmethod
    async def validate_upload_headers(upload_file: UploadFile) -> tuple[bool, str]:
        """
        Validate file upload headers without reading content.
        Used for streaming uploads to validate before processing.
        """
        # 1. Validate filename
        if not upload_file.filename or len(upload_file.filename) > MAX_FILENAME_LENGTH:
            return False, "Invalid filename"

        # 2. Check for path traversal
        if '..' in upload_file.filename or '/' in upload_file.filename or '\\' in upload_file.filename:
            return False, "Invalid filename characters"

        # 3. Validate extension
        ext = Path(upload_file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            return False, f"File type {ext} not allowed"

        # 4. Validate content-type header (basic check)
        content_type = upload_file.content_type or ""
        expected_content_types = {
            '.pdf': ['application/pdf'],
            '.txt': ['text/plain'],
            '.docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
            '.xlsx': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
            '.csv': ['text/csv', 'text/plain', 'application/csv'],
        }

        if content_type not in expected_content_types.get(ext, []):
            # Allow empty content-type for now (will be validated by MIME type later)
            if content_type:
                return False, f"Content-type {content_type} doesn't match extension {ext}"

        return True, "Headers valid"

    @staticmethod
    def validate_temp_file(temp_path: str, original_filename: str) -> tuple[bool, str]:
        """
        Validate a file that has been streamed to temporary storage.
        Performs full content validation on the stored file.
        """
        if not os.path.exists(temp_path):
            return False, f"Temp file does not exist: {temp_path}"

        try:
            # Get file size
            file_size = os.path.getsize(temp_path)
            if file_size > MAX_FILE_SIZE:
                return False, f"File size {file_size} exceeds maximum {MAX_FILE_SIZE}"

            # Read first 2KB for MIME type validation
            with open(temp_path, 'rb') as f:
                content = f.read(2048)

            # Validate MIME type
            mime = magic.from_buffer(content, mime=True)
            ext = Path(original_filename).suffix.lower()

            expected_mimes = {
                '.pdf': ['application/pdf'],
                '.txt': ['text/plain'],
                '.docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
                '.xlsx': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
                '.csv': ['text/csv', 'text/plain'],
            }

            if mime not in expected_mimes.get(ext, []):
                return False, f"MIME type {mime} doesn't match extension {ext}"

            # Additional validation for specific file types
            if ext == '.pdf':
                # Check if it's actually a valid PDF (starts with %PDF-)
                if not content.startswith(b'%PDF-'):
                    return False, "File is not a valid PDF"
            elif ext in ['.docx', '.xlsx']:
                # Check if it's a valid ZIP-based Office document
                try:
                    with zipfile.ZipFile(temp_path, 'r') as zf:
                        # Check for required Office structure
                        if ext == '.docx' and 'word/document.xml' not in zf.namelist():
                            return False, "File is not a valid DOCX"
                        elif ext == '.xlsx' and 'xl/workbook.xml' not in zf.namelist():
                            return False, "File is not a valid XLSX"
                except zipfile.BadZipFile:
                    return False, f"File is not a valid {ext.upper()} file"

            return True, "File validated successfully"

        except Exception as e:
            return False, f"File validation error: {str(e)}"


def sanitize_filename(filename: str) -> str:
    """Remove dangerous characters from filename"""
    filename = os.path.basename(filename)
    filename = re.sub(r'[^\w\s.-]', '', filename)
    name, ext = os.path.splitext(filename)
    name = name[:100]
    return f"{uuid.uuid4().hex[:8]}_{name}{ext}"


def validate_zip_safety(zip_path: str) -> bool:
    """Prevent ZIP bombs"""
    with zipfile.ZipFile(zip_path, 'r') as zf:
        if len(zf.namelist()) > MAX_ZIP_FILES:
            raise HTTPException(400, "ZIP contains too many files")
        total_compressed = sum(info.compress_size for info in zf.infolist())
        total_uncompressed = sum(info.file_size for info in zf.infolist())
        if total_compressed == 0 or total_uncompressed / total_compressed > MAX_ZIP_RATIO:
            raise HTTPException(400, "ZIP compression ratio too high")
        return True
