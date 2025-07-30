from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl, field_validator

from followthemoney.types import registry


class DataResource(BaseModel):
    """A downloadable resource that is part of a dataset."""

    name: str
    url: Optional[HttpUrl] = None
    checksum: Optional[str] = None
    timestamp: Optional[datetime] = None
    mime_type: Optional[str] = None
    title: Optional[str] = None
    size: Optional[int] = None

    @field_validator("mime_type", mode="after")
    @classmethod
    def ensure_mime_type(cls, value: str) -> Optional[str]:
        if not registry.mimetype.validate(value):
            raise ValueError(f"Invalid MIME type: {value!r}")
        return value

    @property
    def mime_type_label(self) -> Optional[str]:
        if self.mime_type is None:
            return None
        return registry.mimetype.caption(self.mime_type)
