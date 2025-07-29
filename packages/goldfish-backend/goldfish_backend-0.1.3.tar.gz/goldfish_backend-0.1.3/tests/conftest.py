"""
Pytest configuration and fixtures
"""
import os
import tempfile
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from faker import Faker
from httpx import AsyncClient
from sqlmodel import Session, SQLModel, create_engine

import goldfish_backend.models.note  # noqa
import goldfish_backend.models.person  # noqa  
import goldfish_backend.models.project  # noqa
import goldfish_backend.models.source_file  # noqa
import goldfish_backend.models.suggested_entity  # noqa
import goldfish_backend.models.task  # noqa
import goldfish_backend.models.topic  # noqa

# Import all models to ensure they're registered
import goldfish_backend.models.user  # noqa

fake = Faker()


@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine for the session"""
    # Create temporary SQLite database
    temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_db.close()

    engine = create_engine(f"sqlite:///{temp_db.name}", echo=False)

    # Create all tables
    SQLModel.metadata.create_all(engine)

    yield engine

    # Cleanup
    os.unlink(temp_db.name)


@pytest.fixture
def db_session(test_engine) -> Generator[Session, None, None]:
    """Create a fresh database session for each test"""
    # Create a new session for each test
    with Session(test_engine) as session:
        yield session
        # Clean up all data after each test
        for table in reversed(SQLModel.metadata.sorted_tables):
            session.exec(table.delete())
        session.commit()


@pytest.fixture
def sample_user(db_session: Session):
    """Create a sample user for testing"""
    from goldfish_backend.core.auth import get_password_hash
    from goldfish_backend.models.user import User

    user = User(
        email=fake.email(),
        hashed_password=get_password_hash("TestPassword123!"),
        full_name=fake.name(),
        bio=fake.text(max_nb_chars=100)
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture
def sample_person(db_session: Session, sample_user):
    """Create a sample person for testing"""
    from goldfish_backend.models.person import Person

    person = Person(
        user_id=sample_user.id,
        name=fake.name(),
        aliases=[fake.first_name(), fake.last_name()],
        importance_score=fake.random.uniform(1.0, 10.0),
        bio=fake.text(),
        email=fake.email()
    )

    db_session.add(person)
    db_session.commit()
    db_session.refresh(person)

    return person


@pytest.fixture
def sample_project(db_session: Session, sample_user):
    """Create a sample project for testing"""
    from goldfish_backend.models.project import Project

    project = Project(
        user_id=sample_user.id,
        name=fake.catch_phrase(),
        description=fake.text(),
        status="active",
        priority_score=fake.random.uniform(1.0, 10.0)
    )

    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    return project


@pytest.fixture
def sample_source_file(db_session: Session, sample_user):
    """Create a sample source file for testing"""
    from datetime import datetime

    from goldfish_backend.models.source_file import SourceFile

    source_file = SourceFile(
        user_id=sample_user.id,
        file_path=f"/test/{fake.file_name()}",
        relative_path=fake.file_name(),
        file_hash=fake.sha256(),
        file_size=fake.random_int(min=100, max=10000),
        last_modified=datetime.utcnow()
    )

    db_session.add(source_file)
    db_session.commit()
    db_session.refresh(source_file)

    return source_file


@pytest.fixture
def sample_note(db_session: Session, sample_user, sample_source_file):
    """Create a sample note for testing"""
    from datetime import datetime

    from goldfish_backend.models.note import Note

    note = Note(
        user_id=sample_user.id,
        source_file_id=sample_source_file.id,
        content=fake.text(),
        content_hash=fake.sha256(),
        snapshot_at=datetime.utcnow(),
        processing_metadata={"source": "test_fixture"}
    )

    db_session.add(note)
    db_session.commit()
    db_session.refresh(note)

    return note


@pytest.fixture
def sample_suggestion(db_session: Session, sample_user, sample_note):
    """Create a sample suggested entity for testing"""
    from goldfish_backend.models.suggested_entity import SuggestedEntity

    suggestion = SuggestedEntity(
        user_id=sample_user.id,
        note_id=sample_note.id,
        entity_type="person",
        name=fake.name(),
        confidence=fake.random.uniform(0.7, 1.0),
        context=fake.sentence(),
        status="pending",
        extraction_metadata={"pattern": "@mention"}
    )

    db_session.add(suggestion)
    db_session.commit()
    db_session.refresh(suggestion)

    return suggestion


@pytest.fixture
def user_service(db_session: Session):
    """Create a UserService instance for testing"""
    from goldfish_backend.services.user_service import UserService
    return UserService(db_session)


@pytest.fixture
def suggestion_service(db_session: Session):
    """Create a SuggestionService instance for testing"""
    from goldfish_backend.services.suggestion_service import SuggestionService
    return SuggestionService(db_session)


@pytest.fixture
def valid_user_data():
    """Generate valid user creation data"""
    from goldfish_backend.models.schemas import UserCreate

    return UserCreate(
        email=fake.email(),
        password="TestPassword123!",
        full_name=fake.name(),
        bio=fake.text(max_nb_chars=200)
    )


@pytest.fixture
def weak_password_user_data():
    """Generate user data with weak password for testing validation"""
    from goldfish_backend.models.schemas import UserCreate

    return UserCreate(
        email=fake.email(),
        password="weak",  # Intentionally weak
        full_name=fake.name()
    )


# Async fixtures for future API testing
@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client with test database"""
    # This fixture is prepared for when we add FastAPI endpoints
    pytest.skip("goldfish-backend is a library package without FastAPI app")


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    """Create an authenticated user and return auth headers"""
    # This will be implemented once we have auth endpoints
    pytest.skip("Authentication endpoints not implemented yet")


# Test configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
