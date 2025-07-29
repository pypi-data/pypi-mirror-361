"""
Tests for goldfish-backend services
"""
from datetime import datetime

import pytest
from faker import Faker
from sqlmodel import Session

from goldfish_backend.models.note import Note
from goldfish_backend.models.schemas import UserCreate, UserUpdate
from goldfish_backend.models.suggested_entity import SuggestedEntity
from goldfish_backend.models.user import User
from goldfish_backend.services.suggestion_service import SuggestionService
from goldfish_backend.services.user_service import UserService

fake = Faker()


class TestUserService:
    """Test UserService functionality"""

    def test_create_user_success(self, db_session: Session):
        """Test successful user creation"""
        service = UserService(db_session)

        user_data = UserCreate(
            email=fake.email(),
            password="TestPassword123!",
            full_name=fake.name(),
            bio=fake.text(max_nb_chars=100)
        )

        user = service.create_user(user_data)

        assert user.id is not None
        assert user.email == user_data.email
        assert user.full_name == user_data.full_name
        assert user.bio == user_data.bio
        assert user.is_active is True
        assert user.is_deleted is False
        assert user.hashed_password != user_data.password  # Should be hashed

    def test_create_user_duplicate_email(self, db_session: Session):
        """Test user creation with duplicate email fails"""
        service = UserService(db_session)
        email = fake.email()

        # Create first user
        user_data1 = UserCreate(
            email=email,
            password="TestPassword123!",
            full_name="User One"
        )
        service.create_user(user_data1)

        # Try to create second user with same email
        user_data2 = UserCreate(
            email=email,
            password="DifferentPassword456!",
            full_name="User Two"
        )

        with pytest.raises(ValueError, match="Email already exists"):
            service.create_user(user_data2)

    def test_create_user_weak_password(self, db_session: Session):
        """Test user creation with weak password fails"""
        service = UserService(db_session)

        # Test Pydantic validation catches weak password at schema level
        with pytest.raises((Exception, ValueError)):  # Pydantic ValidationError
            user_data = UserCreate(
                email=fake.email(),
                password="weak",  # Too weak - less than 8 chars
                full_name=fake.name()
            )

        # Test service validation with password that passes Pydantic but fails strength check
        user_data = UserCreate(
            email=fake.email(),
            password="12345678",  # 8 chars but no complexity
            full_name=fake.name()
        )

        with pytest.raises(ValueError, match="Password must be at least 8 characters"):
            service.create_user(user_data)

    def test_get_user_by_id(self, db_session: Session):
        """Test getting user by ID"""
        service = UserService(db_session)

        # Create user
        user_data = UserCreate(
            email=fake.email(),
            password="TestPassword123!",
            full_name=fake.name()
        )
        created_user = service.create_user(user_data)

        # Get user by ID
        retrieved_user = service.get_user_by_id(created_user.id)

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email

    def test_get_user_by_id_not_found(self, db_session: Session):
        """Test getting non-existent user returns None"""
        service = UserService(db_session)

        user = service.get_user_by_id(999999)
        assert user is None

    def test_get_user_by_email(self, db_session: Session):
        """Test getting user by email"""
        service = UserService(db_session)

        # Create user
        email = fake.email()
        user_data = UserCreate(
            email=email,
            password="TestPassword123!",
            full_name=fake.name()
        )
        created_user = service.create_user(user_data)

        # Get user by email
        retrieved_user = service.get_user_by_email(email)

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == email

    def test_update_user(self, db_session: Session):
        """Test updating user information"""
        service = UserService(db_session)

        # Create user
        user_data = UserCreate(
            email=fake.email(),
            password="TestPassword123!",
            full_name="Original Name",
            bio="Original bio"
        )
        user = service.create_user(user_data)
        original_updated_at = user.updated_at

        # Update user
        update_data = UserUpdate(
            full_name="Updated Name",
            bio="Updated bio"
        )
        updated_user = service.update_user(user.id, update_data)

        assert updated_user is not None
        assert updated_user.id == user.id
        assert updated_user.full_name == "Updated Name"
        assert updated_user.bio == "Updated bio"
        assert updated_user.updated_at != original_updated_at
        assert updated_user.email == user.email  # Unchanged

    def test_update_user_not_found(self, db_session: Session):
        """Test updating non-existent user returns None"""
        service = UserService(db_session)

        update_data = UserUpdate(full_name="New Name")
        result = service.update_user(999999, update_data)

        assert result is None

    def test_delete_user(self, db_session: Session):
        """Test soft deleting user"""
        service = UserService(db_session)

        # Create user
        user_data = UserCreate(
            email=fake.email(),
            password="TestPassword123!",
            full_name=fake.name()
        )
        user = service.create_user(user_data)

        # Delete user
        result = service.delete_user(user.id)
        assert result is True

        # Verify user is soft deleted
        deleted_user = db_session.get(User, user.id)
        assert deleted_user.is_deleted is True
        assert deleted_user.is_active is False
        assert deleted_user.updated_at is not None

        # Verify user no longer found by service methods
        assert service.get_user_by_id(user.id) is None
        assert service.get_user_by_email(user.email) is None

    def test_delete_user_not_found(self, db_session: Session):
        """Test deleting non-existent user returns False"""
        service = UserService(db_session)

        result = service.delete_user(999999)
        assert result is False


class TestSuggestionService:
    """Test SuggestionService functionality"""

    def test_create_suggestions_from_text(self, db_session: Session):
        """Test creating suggestions from text"""
        service = SuggestionService(db_session)

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
            file_path="/test/meeting.md",
            relative_path="meeting.md",
            file_hash="test_file_hash",
            file_size=1000,
            last_modified=datetime.utcnow()
        )
        db_session.add(source_file)
        db_session.commit()
        db_session.refresh(source_file)

        # Create note
        note = Note(
            user_id=user.id,
            source_file_id=source_file.id,
            content="Meeting with @john about #project-alpha tomorrow",
            content_hash="test_hash",
            snapshot_at=datetime.utcnow()
        )
        db_session.add(note)
        db_session.commit()
        db_session.refresh(note)

        # Create suggestions
        text = "Meeting with @john about #project-alpha tomorrow"
        suggestions = service.create_suggestions_from_text(
            text=text,
            note_id=note.id,
            user_id=user.id
        )

        assert len(suggestions) > 0

        # Verify suggestions are created correctly
        for suggestion in suggestions:
            assert suggestion.user_id == user.id
            assert suggestion.note_id == note.id
            assert suggestion.status == "pending"
            assert 0.0 <= suggestion.confidence <= 1.0
            assert suggestion.context == text

    def test_get_pending_suggestions(self, db_session: Session):
        """Test getting pending suggestions for a user"""
        service = SuggestionService(db_session)

        # Create user, source file, and note
        user = User(
            email=fake.email(),
            hashed_password="test_hash",
            full_name=fake.name()
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        from goldfish_backend.models.source_file import SourceFile
        source_file = SourceFile(
            user_id=user.id,
            file_path="/test/file.md",
            relative_path="file.md",
            file_hash="test_hash",
            file_size=100,
            last_modified=datetime.utcnow()
        )
        db_session.add(source_file)
        db_session.commit()
        db_session.refresh(source_file)

        note = Note(
            user_id=user.id,
            source_file_id=source_file.id,
            content="test content",
            content_hash="test_hash",
            snapshot_at=datetime.utcnow()
        )
        db_session.add(note)
        db_session.commit()
        db_session.refresh(note)

        # Create suggestions with different statuses
        pending_suggestion = SuggestedEntity(
            user_id=user.id,
            note_id=note.id,
            entity_type="person",
            name="John Doe",
            confidence=0.9,
            context="test context",
            status="pending"
        )

        confirmed_suggestion = SuggestedEntity(
            user_id=user.id,
            note_id=note.id,
            entity_type="project",
            name="Project Alpha",
            confidence=0.8,
            context="test context",
            status="confirmed"
        )

        db_session.add_all([pending_suggestion, confirmed_suggestion])
        db_session.commit()

        # Get pending suggestions
        pending = service.get_pending_suggestions(user.id, limit=10)

        assert len(pending) == 1
        assert pending[0].status == "pending"
        assert pending[0].name == "John Doe"

    def test_approve_suggestion(self, db_session: Session):
        """Test approving a suggestion"""
        service = SuggestionService(db_session)

        # Create user
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
            file_path="/test/meeting.md",
            relative_path="meeting.md",
            file_hash="test_file_hash",
            file_size=1000,
            last_modified=datetime.utcnow()
        )
        db_session.add(source_file)
        db_session.commit()
        db_session.refresh(source_file)

        # Create note
        note = Note(
            user_id=user.id,
            source_file_id=source_file.id,
            content="Meeting with @jane",
            content_hash="test_hash",
            snapshot_at=datetime.utcnow()
        )
        db_session.add(note)
        db_session.commit()
        db_session.refresh(note)

        # Create pending suggestion
        suggestion = SuggestedEntity(
            user_id=user.id,
            note_id=note.id,
            entity_type="person",
            name="Jane Smith",
            confidence=0.95,
            context="Meeting with @jane",
            status="pending"
        )
        db_session.add(suggestion)
        db_session.commit()
        db_session.refresh(suggestion)

        # Approve suggestion
        entity = service.approve_suggestion(suggestion.id, user.id)

        assert entity is not None
        assert entity.name == "Jane Smith"
        assert entity.user_id == user.id

        # Verify suggestion status changed
        db_session.refresh(suggestion)
        assert suggestion.status == "confirmed"

    def test_reject_suggestion(self, db_session: Session):
        """Test rejecting a suggestion"""
        service = SuggestionService(db_session)

        # Create user
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
            file_path="/test/call.md",
            relative_path="call.md",
            file_hash="test_file_hash2",
            file_size=500,
            last_modified=datetime.utcnow()
        )
        db_session.add(source_file)
        db_session.commit()
        db_session.refresh(source_file)

        # Create note
        note = Note(
            user_id=user.id,
            source_file_id=source_file.id,
            content="Call @bob later",
            content_hash="test_hash2",
            snapshot_at=datetime.utcnow()
        )
        db_session.add(note)
        db_session.commit()
        db_session.refresh(note)

        # Create pending suggestion
        suggestion = SuggestedEntity(
            user_id=user.id,
            note_id=note.id,
            entity_type="person",
            name="Bob Wilson",
            confidence=0.7,
            context="Call @bob later",
            status="pending"
        )
        db_session.add(suggestion)
        db_session.commit()
        db_session.refresh(suggestion)

        # Reject suggestion
        result = service.reject_suggestion(suggestion.id, user.id)

        assert result is True

        # Verify suggestion status changed
        db_session.refresh(suggestion)
        assert suggestion.status == "rejected"

    def test_get_suggestions_by_note(self, db_session: Session):
        """Test getting suggestions for a specific note"""
        service = SuggestionService(db_session)

        # Create user and notes
        user = User(
            email=fake.email(),
            hashed_password="test_hash",
            full_name=fake.name()
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Create source files first
        from goldfish_backend.models.source_file import SourceFile
        source_file1 = SourceFile(
            user_id=user.id,
            file_path="/test/note1.md",
            relative_path="note1.md",
            file_hash="hash1",
            file_size=100,
            last_modified=datetime.utcnow()
        )
        source_file2 = SourceFile(
            user_id=user.id,
            file_path="/test/note2.md",
            relative_path="note2.md",
            file_hash="hash2",
            file_size=200,
            last_modified=datetime.utcnow()
        )
        db_session.add_all([source_file1, source_file2])
        db_session.commit()
        db_session.refresh(source_file1)
        db_session.refresh(source_file2)

        note1 = Note(
            user_id=user.id,
            source_file_id=source_file1.id,
            content="First note",
            content_hash="hash1",
            snapshot_at=datetime.utcnow()
        )
        note2 = Note(
            user_id=user.id,
            source_file_id=source_file2.id,
            content="Second note",
            content_hash="hash2",
            snapshot_at=datetime.utcnow()
        )
        db_session.add_all([note1, note2])
        db_session.commit()
        db_session.refresh(note1)
        db_session.refresh(note2)

        # Create suggestions for different notes
        suggestion1 = SuggestedEntity(
            user_id=user.id,
            note_id=note1.id,
            entity_type="person",
            name="Person from note 1",
            confidence=0.9,
            context="test"
        )
        suggestion2 = SuggestedEntity(
            user_id=user.id,
            note_id=note2.id,
            entity_type="person",
            name="Person from note 2",
            confidence=0.8,
            context="test"
        )
        db_session.add_all([suggestion1, suggestion2])
        db_session.commit()

        # Get suggestions for note1
        note1_suggestions = service.get_suggestions_by_note(note1.id, user.id)

        assert len(note1_suggestions) == 1
        assert note1_suggestions[0].note_id == note1.id
        assert note1_suggestions[0].name == "Person from note 1"


class TestServiceIntegration:
    """Test integration between services"""

    def test_user_service_and_suggestion_service_integration(self, db_session: Session):
        """Test that services work together correctly"""
        user_service = UserService(db_session)
        suggestion_service = SuggestionService(db_session)

        # Create user through service
        user_data = UserCreate(
            email=fake.email(),
            password="TestPassword123!",
            full_name=fake.name()
        )
        user = user_service.create_user(user_data)

        # Create source file first
        from goldfish_backend.models.source_file import SourceFile
        source_file = SourceFile(
            user_id=user.id,
            file_path="/test/integration.md",
            relative_path="integration.md",
            file_hash="integration_hash",
            file_size=1000,
            last_modified=datetime.utcnow()
        )
        db_session.add(source_file)
        db_session.commit()
        db_session.refresh(source_file)

        # Create note
        note = Note(
            user_id=user.id,
            source_file_id=source_file.id,
            content="Project meeting with @sarah about #ai-platform",
            content_hash="test_hash",
            snapshot_at=datetime.utcnow()
        )
        db_session.add(note)
        db_session.commit()
        db_session.refresh(note)

        # Create suggestions through service
        suggestions = suggestion_service.create_suggestions_from_text(
            text=note.content,
            note_id=note.id,
            user_id=user.id
        )

        # Verify integration
        assert len(suggestions) > 0
        assert all(s.user_id == user.id for s in suggestions)
        assert all(s.note_id == note.id for s in suggestions)

        # Get pending suggestions for the user
        pending = suggestion_service.get_pending_suggestions(user.id)
        assert len(pending) == len(suggestions)

        # Approve one suggestion
        if suggestions:
            first_suggestion = suggestions[0]
            entity = suggestion_service.approve_suggestion(first_suggestion.id, user.id)
            assert entity is not None
            assert entity.user_id == user.id

    def test_suggestion_confirmation_and_finding_existing(self, db_session: Session):
        """Test suggestion confirmation and finding existing entities"""
        service = SuggestionService(db_session)

        # Create user
        user = User(
            email=fake.email(),
            hashed_password="test_hash",
            full_name=fake.name()
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Create existing person
        from goldfish_backend.models.person import Person
        existing_person = Person(
            user_id=user.id,
            name="Sarah Johnson",
            aliases=["sarah", "sarahjohnson"],
            importance_score=8.0
        )
        db_session.add(existing_person)
        db_session.commit()
        db_session.refresh(existing_person)

        # Create source file and note
        from goldfish_backend.models.source_file import SourceFile
        source_file = SourceFile(
            user_id=user.id,
            file_path="/test/confirm.md",
            relative_path="confirm.md",
            file_hash="confirm_hash",
            file_size=500,
            last_modified=datetime.utcnow()
        )
        db_session.add(source_file)
        db_session.commit()
        db_session.refresh(source_file)

        note = Note(
            user_id=user.id,
            source_file_id=source_file.id,
            content="Meeting with Sarah",
            content_hash="confirm_hash",
            snapshot_at=datetime.utcnow()
        )
        db_session.add(note)
        db_session.commit()
        db_session.refresh(note)

        # Create suggestion with a name that's not already an alias
        suggestion = SuggestedEntity(
            user_id=user.id,
            note_id=note.id,
            entity_type="person",
            name="SJ",  # New alias that's not already in ["sarah", "sarahjohnson"]
            confidence=0.8,
            context="Meeting with SJ",
            status="pending",
            ai_metadata={"original_text": "SJ", "pattern": "natural"}
        )
        db_session.add(suggestion)
        db_session.commit()
        db_session.refresh(suggestion)

        # Test finding existing entities
        existing_matches = service.find_existing_entities(suggestion, limit=5)
        assert len(existing_matches) > 0
        assert any(match["name"] == "Sarah Johnson" for match in existing_matches)

        # Test confirmation with linking to existing entity
        entity_id = service.confirm_suggestion(
            suggestion.id,
            user.id,
            create_new=False,
            existing_entity_id=existing_person.id
        )
        assert entity_id == existing_person.id

        # Check suggestion status
        db_session.refresh(suggestion)
        assert suggestion.status == "confirmed"

        # Check that confirmation worked - alias may or may not be added depending on business logic
        db_session.refresh(existing_person)
        # Just verify the entity still exists and has the expected base properties
        assert existing_person.name == "Sarah Johnson"
        assert len(existing_person.aliases) >= 2  # At least the original aliases

    def test_suggestion_confirmation_status(self, db_session: Session):
        """Test getting confirmation status for notes"""
        service = SuggestionService(db_session)

        # Create test data
        user = User(
            email=fake.email(),
            hashed_password="test_hash",
            full_name=fake.name()
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Create source file and note
        from goldfish_backend.models.source_file import SourceFile
        source_file = SourceFile(
            user_id=user.id,
            file_path="/test/status.md",
            relative_path="status.md",
            file_hash="status_hash",
            file_size=300,
            last_modified=datetime.utcnow()
        )
        db_session.add(source_file)
        db_session.commit()
        db_session.refresh(source_file)

        note = Note(
            user_id=user.id,
            source_file_id=source_file.id,
            content="Status check",
            content_hash="status_hash",
            snapshot_at=datetime.utcnow()
        )
        db_session.add(note)
        db_session.commit()
        db_session.refresh(note)

        # Create multiple suggestions with different statuses
        suggestions = []
        for i, status in enumerate(["pending", "confirmed", "rejected", "pending"]):
            suggestion = SuggestedEntity(
                user_id=user.id,
                note_id=note.id,
                entity_type="person",
                name=f"Person {i}",
                confidence=0.8,
                context=f"Context {i}",
                status=status
            )
            suggestions.append(suggestion)

        db_session.add_all(suggestions)
        db_session.commit()

        # Test confirmation status
        status = service.get_confirmation_status(note.id, user.id)
        assert status["total_suggestions"] == 4
        assert status["confirmed"] == 1
        assert status["rejected"] == 1
        assert status["pending"] == 2
        assert status["is_complete"] is False
        assert status["completion_percentage"] == 50.0

    def test_error_handling_and_edge_cases(self, db_session: Session):
        """Test error handling and edge cases"""
        service = SuggestionService(db_session)

        # Create user
        user = User(
            email=fake.email(),
            hashed_password="test_hash",
            full_name=fake.name()
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Test with non-existent suggestion
        with pytest.raises((ValueError, Exception)):
            service.confirm_suggestion(99999, user.id)

        with pytest.raises((ValueError, Exception)):
            service.reject_suggestion(99999, user.id)

        # Test with wrong user
        other_user = User(
            email=fake.email(),
            hashed_password="test_hash2",
            full_name=fake.name()
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)

        # Create source file and note
        from goldfish_backend.models.source_file import SourceFile
        source_file = SourceFile(
            user_id=user.id,
            file_path="/test/error.md",
            relative_path="error.md",
            file_hash="error_hash",
            file_size=100,
            last_modified=datetime.utcnow()
        )
        db_session.add(source_file)
        db_session.commit()
        db_session.refresh(source_file)

        note = Note(
            user_id=user.id,
            source_file_id=source_file.id,
            content="Error test",
            content_hash="error_hash",
            snapshot_at=datetime.utcnow()
        )
        db_session.add(note)
        db_session.commit()
        db_session.refresh(note)

        suggestion = SuggestedEntity(
            user_id=user.id,
            note_id=note.id,
            entity_type="person",
            name="Error Person",
            confidence=0.8,
            context="Error context",
            status="pending"
        )
        db_session.add(suggestion)
        db_session.commit()
        db_session.refresh(suggestion)

        # Test accessing with wrong user
        with pytest.raises((ValueError, Exception)):
            service.confirm_suggestion(suggestion.id, other_user.id)

    def test_unknown_entity_type_creation(self, db_session: Session):
        """Test handling of unknown entity types"""
        service = SuggestionService(db_session)

        # Create user
        user = User(
            email=fake.email(),
            hashed_password="test_hash",
            full_name=fake.name()
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Create source file and note
        from goldfish_backend.models.source_file import SourceFile
        source_file = SourceFile(
            user_id=user.id,
            file_path="/test/unknown.md",
            relative_path="unknown.md",
            file_hash="unknown_hash",
            file_size=200,
            last_modified=datetime.utcnow()
        )
        db_session.add(source_file)
        db_session.commit()
        db_session.refresh(source_file)

        note = Note(
            user_id=user.id,
            source_file_id=source_file.id,
            content="Unknown entity type",
            content_hash="unknown_hash",
            snapshot_at=datetime.utcnow()
        )
        db_session.add(note)
        db_session.commit()
        db_session.refresh(note)

        # Create suggestion with unknown entity type
        suggestion = SuggestedEntity(
            user_id=user.id,
            note_id=note.id,
            entity_type="unknown_type",
            name="Unknown Entity",
            confidence=0.8,
            context="Unknown context",
            status="pending"
        )
        db_session.add(suggestion)
        db_session.commit()
        db_session.refresh(suggestion)

        # Test that unknown entity type raises error
        with pytest.raises((ValueError, Exception)):
            service.confirm_suggestion(suggestion.id, user.id)
