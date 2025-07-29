"""
Tests for goldfish-backend models
"""
from datetime import datetime

import pytest
from faker import Faker
from sqlmodel import Session, select

from goldfish_backend.models.note import Note
from goldfish_backend.models.person import Person
from goldfish_backend.models.project import Project
from goldfish_backend.models.suggested_entity import SuggestedEntity
from goldfish_backend.models.user import User

fake = Faker()


class TestUserModel:
    """Test User model functionality"""

    def test_create_user_basic(self, db_session: Session):
        """Test basic user creation"""
        email = fake.email()
        user = User(
            email=email,
            hashed_password="hashed_password_123",
            full_name=fake.name(),
            bio=fake.text(max_nb_chars=200)
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.email == email
        assert user.is_active is True
        assert user.is_deleted is False
        assert isinstance(user.created_at, datetime)

    def test_user_email_unique(self, db_session: Session):
        """Test that user emails are unique"""
        email = fake.email()

        # Create first user
        user1 = User(
            email=email,
            hashed_password="hash1",
            full_name="User One"
        )
        db_session.add(user1)
        db_session.commit()

        # Try to create second user with same email
        user2 = User(
            email=email,
            hashed_password="hash2",
            full_name="User Two"
        )
        db_session.add(user2)

        with pytest.raises((Exception, ValueError)):  # Should raise integrity error
            db_session.commit()
        
        # Rollback the failed transaction
        db_session.rollback()

    def test_user_defaults(self, db_session: Session):
        """Test user model defaults"""
        user = User(
            email=fake.email(),
            hashed_password="test_hash",
            full_name=fake.name()
        )

        assert user.bio is None
        assert user.updated_at is None
        assert user.is_active is True
        assert user.is_deleted is False
        assert user.created_at is not None


class TestPersonModel:
    """Test Person model functionality"""

    def test_create_person(self, db_session: Session):
        """Test basic person creation"""
        # Create a user first
        user = User(
            email=fake.email(),
            hashed_password="test_hash",
            full_name=fake.name()
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Create person
        person_name = fake.name()
        person = Person(
            user_id=user.id,
            name=person_name,
            aliases=["alias1", "alias2"],
            importance_score=7.5,
            bio=fake.text(),
            email=fake.email()
        )

        db_session.add(person)
        db_session.commit()
        db_session.refresh(person)

        assert person.id is not None
        assert person.user_id == user.id
        assert person.name == person_name
        assert person.aliases == ["alias1", "alias2"]
        assert person.importance_score == 7.5
        assert person.is_deleted is False
        assert isinstance(person.created_at, datetime)

    def test_person_defaults(self, db_session: Session):
        """Test person model defaults"""
        # Create user first
        user = User(
            email=fake.email(),
            hashed_password="test_hash",
            full_name=fake.name()
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Create person with minimal data
        person = Person(
            user_id=user.id,
            name=fake.name()
        )

        assert person.aliases == []
        assert person.importance_score == 1.0
        assert person.bio is None
        assert person.email is None
        assert person.phone is None
        assert person.is_deleted is False

    def test_person_importance_score_validation(self, db_session: Session):
        """Test importance score validation (0-10 range)"""
        # Create user first
        user = User(
            email=fake.email(),
            hashed_password="test_hash",
            full_name=fake.name()
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Test valid scores
        for score in [0.0, 5.5, 10.0]:
            person = Person(
                user_id=user.id,
                name=fake.name(),
                importance_score=score
            )
            db_session.add(person)
            db_session.commit()
            assert person.importance_score == score
            db_session.delete(person)
            db_session.commit()


class TestProjectModel:
    """Test Project model functionality"""

    def test_create_project(self, db_session: Session):
        """Test basic project creation"""
        # Create user first
        user = User(
            email=fake.email(),
            hashed_password="test_hash",
            full_name=fake.name()
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Create project
        project_name = fake.company()
        project = Project(
            user_id=user.id,
            name=project_name,
            description=fake.text(),
            status="active",
            priority_score=8.0
        )

        db_session.add(project)
        db_session.commit()
        db_session.refresh(project)

        assert project.id is not None
        assert project.user_id == user.id
        assert project.name == project_name
        assert project.status == "active"
        assert project.priority_score == 8.0
        assert project.is_deleted is False


class TestNoteModel:
    """Test Note model functionality"""

    def test_create_note(self, db_session: Session):
        """Test basic note creation"""
        # Create user first
        user = User(
            email=fake.email(),
            hashed_password="test_hash",
            full_name=fake.name()
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Create source file first
        from goldfish_backend.models.source_file import SourceFile
        source_file = SourceFile(
            user_id=user.id,
            file_path="/test/path.md",
            relative_path="path.md",
            file_hash="test_file_hash",
            file_size=1000,
            last_modified=datetime.utcnow()
        )
        db_session.add(source_file)
        db_session.commit()
        db_session.refresh(source_file)

        # Create note
        content = fake.text()
        note = Note(
            user_id=user.id,
            source_file_id=source_file.id,
            content=content,
            content_hash="test_hash",
            snapshot_at=datetime.utcnow(),
            processing_metadata={"source": "test"}
        )

        db_session.add(note)
        db_session.commit()
        db_session.refresh(note)

        assert note.id is not None
        assert note.user_id == user.id
        assert note.source_file_id == source_file.id
        assert note.content == content
        assert note.processing_metadata == {"source": "test"}
        assert note.is_deleted is False


class TestSuggestedEntityModel:
    """Test SuggestedEntity model functionality"""

    def test_create_suggested_entity(self, db_session: Session):
        """Test basic suggested entity creation"""
        # Create user first
        user = User(
            email=fake.email(),
            hashed_password="test_hash",
            full_name=fake.name()
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Create source file and note first
        from goldfish_backend.models.source_file import SourceFile
        source_file = SourceFile(
            user_id=user.id,
            file_path="/test/path.md",
            relative_path="path.md",
            file_hash="test_file_hash",
            file_size=1000,
            last_modified=datetime.utcnow()
        )
        db_session.add(source_file)
        db_session.commit()
        db_session.refresh(source_file)

        note = Note(
            user_id=user.id,
            source_file_id=source_file.id,
            content="Meeting with @john tomorrow",
            content_hash="test_hash",
            snapshot_at=datetime.utcnow()
        )
        db_session.add(note)
        db_session.commit()
        db_session.refresh(note)

        # Create suggested entity
        suggestion = SuggestedEntity(
            user_id=user.id,
            note_id=note.id,
            entity_type="person",
            name="John Doe",
            confidence=0.95,
            context="Meeting with @john tomorrow",
            status="pending",
            ai_metadata={"pattern": "@mention"}
        )

        db_session.add(suggestion)
        db_session.commit()
        db_session.refresh(suggestion)

        assert suggestion.id is not None
        assert suggestion.user_id == user.id
        assert suggestion.note_id == note.id
        assert suggestion.entity_type == "person"
        assert suggestion.name == "John Doe"
        assert suggestion.confidence == 0.95
        assert suggestion.status == "pending"
        assert suggestion.ai_metadata == {"pattern": "@mention"}

    def test_suggested_entity_confidence_validation(self, db_session: Session):
        """Test confidence score validation (0-1 range)"""
        # Create user first
        user = User(
            email=fake.email(),
            hashed_password="test_hash",
            full_name=fake.name()
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Create source file and note first
        from goldfish_backend.models.source_file import SourceFile
        source_file = SourceFile(
            user_id=user.id,
            file_path="/test/path.md",
            relative_path="path.md",
            file_hash="test_file_hash",
            file_size=1000,
            last_modified=datetime.utcnow()
        )
        db_session.add(source_file)
        db_session.commit()
        db_session.refresh(source_file)

        note = Note(
            user_id=user.id,
            source_file_id=source_file.id,
            content="test context",
            content_hash="test_hash",
            snapshot_at=datetime.utcnow()
        )
        db_session.add(note)
        db_session.commit()
        db_session.refresh(note)

        # Test valid confidence scores
        for confidence in [0.0, 0.5, 1.0]:
            suggestion = SuggestedEntity(
                user_id=user.id,
                note_id=note.id,
                entity_type="person",
                name="Test",
                confidence=confidence,
                context="test context"
            )
            db_session.add(suggestion)
            db_session.commit()
            assert suggestion.confidence == confidence
            db_session.delete(suggestion)
            db_session.commit()


class TestModelRelationships:
    """Test relationships between models"""

    def test_user_can_have_multiple_entities(self, db_session: Session):
        """Test that a user can have multiple people, projects, etc."""
        # Create user
        user = User(
            email=fake.email(),
            hashed_password="test_hash",
            full_name=fake.name()
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Create multiple entities for the user
        person1 = Person(user_id=user.id, name="Person 1")
        person2 = Person(user_id=user.id, name="Person 2")
        project1 = Project(user_id=user.id, name="Project 1")
        project2 = Project(user_id=user.id, name="Project 2")

        db_session.add_all([person1, person2, project1, project2])
        db_session.commit()

        # Verify user has multiple entities
        people = db_session.exec(
            select(Person).where(Person.user_id == user.id)
        ).all()
        projects = db_session.exec(
            select(Project).where(Project.user_id == user.id)
        ).all()

        assert len(people) == 2
        assert len(projects) == 2
        assert all(p.user_id == user.id for p in people)
        assert all(p.user_id == user.id for p in projects)

    def test_soft_delete_filtering(self, db_session: Session):
        """Test that soft-deleted entities are properly filtered"""
        # Create user and person
        user = User(
            email=fake.email(),
            hashed_password="test_hash",
            full_name=fake.name()
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        person = Person(user_id=user.id, name="Test Person")
        db_session.add(person)
        db_session.commit()
        db_session.refresh(person)

        # Verify person exists
        active_people = db_session.exec(
            select(Person).where(Person.user_id == user.id, Person.is_deleted == False)
        ).all()
        assert len(active_people) == 1

        # Soft delete person
        person.is_deleted = True
        db_session.add(person)
        db_session.commit()

        # Verify person is filtered out
        active_people = db_session.exec(
            select(Person).where(Person.user_id == user.id, Person.is_deleted == False)
        ).all()
        assert len(active_people) == 0

        # But still exists when not filtering
        all_people = db_session.exec(
            select(Person).where(Person.user_id == user.id)
        ).all()
        assert len(all_people) == 1
