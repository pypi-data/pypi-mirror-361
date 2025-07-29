"""
Database models for Goldfish backend
"""

# Import all models for SQLModel table creation
from .entity_learning import EntityLearning
from .note import Note
from .person import Person
from .project import Project
from .relationships import (
    NotePerson,
    NoteProject,
    NoteTopic,
    TaskPerson,
    TaskProject,
    TaskTopic,
    TopicPerson,
    TopicProject,
    TopicRelationship,
)
from .source_file import SourceFile
from .suggested_entity import SuggestedEntity
from .task import Task
from .topic import Topic
from .user import User

__all__ = [
    "User",
    "SourceFile",
    "Note",
    "Person",
    "Project",
    "Topic",
    "Task",
    "SuggestedEntity",
    "EntityLearning",
    "TaskPerson",
    "TaskProject",
    "TaskTopic",
    "NotePerson",
    "NoteProject",
    "NoteTopic",
    "TopicRelationship",
    "TopicPerson",
    "TopicProject",
]
