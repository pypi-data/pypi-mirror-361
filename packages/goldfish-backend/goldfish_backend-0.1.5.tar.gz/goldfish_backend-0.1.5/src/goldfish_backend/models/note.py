"""
Note model for immutable snapshots of processed file content
"""
from datetime import datetime
from typing import Any

from sqlmodel import JSON, Column, Field, SQLModel, String, Text


class Note(SQLModel, table=True):
    """Note table for immutable snapshots of processed file content"""

    __tablename__ = "notes"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    source_file_id: int = Field(foreign_key="source_files.id")
    content: str = Field(sa_column=Column(Text))
    content_hash: str = Field(sa_column=Column(String(64), index=True))
    snapshot_at: datetime

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Processing metadata and flags
    processing_metadata: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    is_deleted: bool = Field(default=False)

    class Config:
        """SQLModel configuration"""
        from_attributes = True
