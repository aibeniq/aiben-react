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
