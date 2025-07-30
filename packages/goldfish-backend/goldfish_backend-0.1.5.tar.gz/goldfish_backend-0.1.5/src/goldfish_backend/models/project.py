"""
Project model for organizing work and goals
"""
from datetime import datetime

from sqlmodel import JSON, Column, Field, SQLModel, String, Text


class Project(SQLModel, table=True):
    """Project entity table for work and goal organization"""

    __tablename__ = "projects"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    name: str = Field(sa_column=Column(String(255)))
    aliases: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    description: str | None = Field(default=None, sa_column=Column(Text))
    deadline: datetime | None = None
    status: str = Field(default="active", sa_column=Column(String(20)))  # active, completed, archived, on_hold
    priority_score: float = Field(default=1.0, ge=0.0, le=10.0)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None

    # Status flags
    is_deleted: bool = Field(default=False)

    class Config:
        """SQLModel configuration"""
        from_attributes = True
