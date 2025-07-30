from typing import Any, Dict, Hashable, Optional

from pydantic import BaseModel, Field


class TusUploadParams(BaseModel):
    metadata: dict[Hashable, str]
    size: int | None
    offset: int = 0
    upload_part: int = 0
    created_at: str
    defer_length: bool = False
    upload_chunk_size: int = 0
    expires: float | str | None
    error: str | None = None
    
    # Allow arbitrary additional fields for external applications
    class Config:
        extra = "allow"
    
    def __init__(self, **data):
        super().__init__(**data)
    
    def get_custom_field(self, field_name: str, default: Any = None) -> Any:
        """Get a custom field added by external applications"""
        return getattr(self, field_name, default)
    
    def set_custom_field(self, field_name: str, value: Any) -> None:
        """Set a custom field for external applications"""
        setattr(self, field_name, value)
    
    def has_custom_field(self, field_name: str) -> bool:
        """Check if a custom field exists"""
        return hasattr(self, field_name)
