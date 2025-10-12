from typing import Any
from uuid import UUID
import re
from fastapi import HTTPException


class InputValidator:
    """Input validation utilities for SQL injection prevention and data sanitization"""

    @staticmethod
    def validate_uuid(value: str) -> UUID:
        """Validate and convert UUID strings"""
        try:
            return UUID(value)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid UUID format")

    @staticmethod
    def validate_alphanumeric(value: str, max_length: int = 100) -> str:
        """Validate alphanumeric strings with underscores and dashes"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', value):
            raise HTTPException(status_code=400, detail="Invalid characters in input")
        if len(value) > max_length:
            raise HTTPException(status_code=400, detail=f"Input exceeds {max_length} characters")
        return value

    @staticmethod
    def validate_email(value: str) -> str:
        """Validate email format"""
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            raise HTTPException(status_code=400, detail="Invalid email format")
        if len(value) > 254:  # RFC 5321 limit
            raise HTTPException(status_code=400, detail="Email address too long")
        return value

    @staticmethod
    def validate_sql_safe_string(value: str, max_length: int = 255) -> str:
        """Validate strings that will be used in SQL queries"""
        if not isinstance(value, str):
            raise HTTPException(status_code=400, detail="Input must be a string")

        # Remove any SQL injection attempts
        dangerous_patterns = [
            r';\s*--',  # Semicolon followed by comment
            r';\s*/\*',  # Semicolon followed by block comment
            r'union\s+select',  # UNION SELECT
            r'/\*.*\*/',  # Block comments
            r'--.*$',  # Line comments
            r';\s*drop',  # DROP statements
            r';\s*delete',  # DELETE statements
            r';\s*update',  # UPDATE statements
            r';\s*insert',  # INSERT statements
        ]

        value_lower = value.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, value_lower, re.IGNORECASE):
                raise HTTPException(status_code=400, detail="Invalid input detected")

        if len(value) > max_length:
            raise HTTPException(status_code=400, detail=f"Input exceeds {max_length} characters")

        return value

    @staticmethod
    def validate_positive_integer(value: Any) -> int:
        """Validate positive integers for pagination/limit parameters"""
        try:
            int_value = int(value)
            if int_value <= 0:
                raise ValueError
            if int_value > 10000:  # Reasonable upper limit
                raise HTTPException(status_code=400, detail="Value too large")
            return int_value
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid integer value")

    @staticmethod
    def validate_sort_field(value: str, allowed_fields: list[str]) -> str:
        """Validate sort field names"""
        if value not in allowed_fields:
            raise HTTPException(status_code=400, detail=f"Invalid sort field: {value}")
        return value

    @staticmethod
    def validate_sort_order(value: str) -> str:
        """Validate sort order (asc/desc)"""
        if value.lower() not in ['asc', 'desc']:
            raise HTTPException(status_code=400, detail="Sort order must be 'asc' or 'desc'")
        return value.lower()
