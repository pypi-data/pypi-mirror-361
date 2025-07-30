"""
Topic model for research, learning, and knowledge organization
"""
from datetime import datetime

from sqlmodel import JSON, Column, Field, SQLModel, String, Text


class Topic(SQLModel, table=True):
    """Topic entity table for research and knowledge organization"""

    __tablename__ = "topics"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    name: str = Field(sa_column=Column(String(255)))
    aliases: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    description: str | None = Field(default=None, sa_column=Column(Text))
    category: str | None = Field(default=None, sa_column=Column(String(100)))
    research_score: float = Field(default=1.0, ge=0.0, le=10.0)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None

    # Status flags
    is_deleted: bool = Field(default=False)

    class Config:
        """SQLModel configuration"""
        from_attributes = True
