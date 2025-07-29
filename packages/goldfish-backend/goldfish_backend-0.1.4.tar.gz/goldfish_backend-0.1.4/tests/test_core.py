"""
Tests for goldfish-backend core functionality
"""
import os
import tempfile
from datetime import datetime, timedelta

from sqlmodel import Session, SQLModel, create_engine

from goldfish_backend.core.auth import (
    AuthConfig,
    authenticate_user,
    create_access_token,
    get_password_hash,
    validate_password_strength,
    verify_password,
)
from goldfish_backend.core.database import engine
from goldfish_backend.models.user import User


class TestAuthFunctionality:
    """Test authentication core functions"""

    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "TestPassword123!"

        # Hash password
        hashed = get_password_hash(password)

        # Verify password
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False
        assert hashed != password  # Should be different from original

    def test_password_strength_validation(self):
        """Test password strength validation"""
        # Valid passwords
        valid_passwords = [
            "TestPassword123!",
            "ComplexP@ssw0rd",
            "MySecure#Pass1",
            "Str0ng!Password"
        ]

        for password in valid_passwords:
            assert validate_password_strength(password) is True, f"Password '{password}' should be valid"

        # Invalid passwords
        invalid_passwords = [
            "weak",                    # Too short
            "password",                # No uppercase, no digits, no special chars
            "PASSWORD",                # No lowercase, no digits, no special chars
            "Password",                # No digits, no special chars
            "Password123",             # No special chars
            "Password!",               # No digits
            "12345678!",               # No letters
            "longpasswordwithoutuppercase123!",  # No uppercase
        ]

        for password in invalid_passwords:
            assert validate_password_strength(password) is False, f"Password '{password}' should be invalid"

    def test_jwt_token_creation_and_verification(self):
        """Test JWT token creation"""
        # Test data
        user_email = "test@example.com"
        data = {"sub": user_email}

        # Create token
        token = create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 0

        # Create token with custom expiration
        custom_expiry = timedelta(minutes=60)
        custom_token = create_access_token(data, expires_delta=custom_expiry)
        assert isinstance(custom_token, str)
        assert custom_token != token  # Should be different due to different expiry

    def test_authenticate_user_success(self, db_session: Session):
        """Test successful user authentication"""
        # Create user with hashed password
        password = "TestPassword123!"
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash(password),
            full_name="Test User"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Test authentication
        result = authenticate_user("test@example.com", password, user)
        assert result == user
        assert isinstance(result, User)

    def test_authenticate_user_wrong_password(self, db_session: Session):
        """Test user authentication with wrong password"""
        # Create user
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("correct_password"),
            full_name="Test User"
        )

        # Test authentication with wrong password
        result = authenticate_user("test@example.com", "wrong_password", user)
        assert result is False

    def test_authenticate_user_not_found(self):
        """Test user authentication when user doesn't exist"""
        result = authenticate_user("nonexistent@example.com", "password", None)
        assert result is False

    def test_auth_config(self):
        """Test authentication configuration"""
        config = AuthConfig()

        assert config.secret_key is not None
        assert config.algorithm == "HS256"
        assert isinstance(config.access_token_expire_minutes, int)
        assert config.access_token_expire_minutes > 0

    def test_auth_config_environment_variables(self):
        """Test auth config reads from environment variables"""
        # Set environment variables
        test_secret = "test-secret-key-123"
        test_expiry = "60"

        os.environ["SECRET_KEY"] = test_secret
        os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = test_expiry

        try:
            config = AuthConfig()
            assert config.secret_key == test_secret
            assert config.access_token_expire_minutes == 60
        finally:
            # Clean up environment
            os.environ.pop("SECRET_KEY", None)
            os.environ.pop("ACCESS_TOKEN_EXPIRE_MINUTES", None)


class TestDatabaseFunctionality:
    """Test database core functions"""

    def test_create_db_and_tables(self):
        """Test database and table creation"""
        # Create temporary database
        temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        temp_db.close()

        try:
            # Create engine with temporary database
            test_engine = create_engine(f"sqlite:///{temp_db.name}", echo=False)

            # Test that we can create tables without errors
            import goldfish_backend.models  # noqa - Import to register models
            SQLModel.metadata.create_all(test_engine)

            # Verify tables exist by creating a session and user
            with Session(test_engine) as session:
                user = User(
                    email="test@example.com",
                    hashed_password="test_hash",
                    full_name="Test User"
                )
                session.add(user)
                session.commit()
                session.refresh(user)

                assert user.id is not None

        finally:
            # Cleanup
            os.unlink(temp_db.name)

    def test_database_engine_exists(self):
        """Test that database engine is properly configured"""

        assert engine is not None
        assert hasattr(engine, 'connect')
        assert hasattr(engine, 'url')

    def test_database_session_management(self):
        """Test database session creation and management"""
        # Create temporary database for testing
        temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        temp_db.close()

        try:
            test_engine = create_engine(f"sqlite:///{temp_db.name}", echo=False)

            # Import models to register them
            import goldfish_backend.models  # noqa
            SQLModel.metadata.create_all(test_engine)

            # Test session creation and usage
            with Session(test_engine) as session:
                # Create user
                user = User(
                    email="session_test@example.com",
                    hashed_password="test_hash",
                    full_name="Session Test User"
                )
                session.add(user)
                session.commit()
                session.refresh(user)

                # Verify user was created
                assert user.id is not None
                assert user.email == "session_test@example.com"

            # Test that session is properly closed (new session should work)
            with Session(test_engine) as new_session:
                from sqlmodel import select

                # Query user from new session
                statement = select(User).where(User.email == "session_test@example.com")
                retrieved_user = new_session.exec(statement).first()

                assert retrieved_user is not None
                assert retrieved_user.email == "session_test@example.com"

        finally:
            # Cleanup
            os.unlink(temp_db.name)


class TestCoreIntegration:
    """Test integration between core components"""

    def test_auth_and_database_integration(self, db_session: Session):
        """Test that authentication works with database"""
        # Create user with proper password hashing
        email = "integration_test@example.com"
        password = "TestPassword123!"

        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name="Integration Test User"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Test full authentication flow
        # 1. Verify password hashing worked
        assert verify_password(password, user.hashed_password) is True

        # 2. Test user authentication
        auth_result = authenticate_user(email, password, user)
        assert auth_result == user

        # 3. Create JWT token for authenticated user
        token_data = {"sub": user.email, "user_id": user.id}
        token = create_access_token(token_data)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_password_change_workflow(self, db_session: Session):
        """Test complete password change workflow"""
        # Create user
        email = "password_change_test@example.com"
        old_password = "OldPassword123!"
        new_password = "NewPassword456!"

        user = User(
            email=email,
            hashed_password=get_password_hash(old_password),
            full_name="Password Change Test User"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Verify old password works
        assert authenticate_user(email, old_password, user) == user
        assert authenticate_user(email, new_password, user) is False

        # Change password
        user.hashed_password = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Verify new password works and old doesn't
        assert authenticate_user(email, new_password, user) == user
        assert authenticate_user(email, old_password, user) is False

    def test_user_lifecycle_with_auth(self, db_session: Session):
        """Test complete user lifecycle with authentication"""
        # 1. Create user with strong password
        email = "lifecycle_test@example.com"
        password = "LifecycleTest123!"

        # Validate password first
        assert validate_password_strength(password) is True

        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name="Lifecycle Test User",
            is_active=True,
            is_deleted=False
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # 2. Authenticate active user
        auth_result = authenticate_user(email, password, user)
        assert auth_result == user

        # 3. Deactivate user
        user.is_active = False
        user.updated_at = datetime.utcnow()
        db_session.add(user)
        db_session.commit()

        # Note: Authentication should still work for deactivated users
        # (application logic should check is_active separately)
        auth_result = authenticate_user(email, password, user)
        assert auth_result == user
        assert user.is_active is False

        # 4. Soft delete user
        user.is_deleted = True
        user.updated_at = datetime.utcnow()
        db_session.add(user)
        db_session.commit()

        # Authentication should still work (soft delete doesn't affect auth)
        # but application should check is_deleted flag
        auth_result = authenticate_user(email, password, user)
        assert auth_result == user
        assert user.is_deleted is True


class TestSecurityFeatures:
    """Test security-related functionality"""

    def test_password_hash_uniqueness(self):
        """Test that same password produces different hashes"""
        password = "TestPassword123!"

        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Hashes should be different (due to salt)
        assert hash1 != hash2

        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_token_contains_no_sensitive_data(self):
        """Test that JWT tokens don't contain sensitive information"""
        import base64
        import json

        # Create token with user data
        user_data = {
            "sub": "test@example.com",
            "user_id": 123
        }
        token = create_access_token(user_data)

        # Decode token payload (without verification, just to check contents)
        # JWT format: header.payload.signature
        parts = token.split('.')
        assert len(parts) == 3

        # Decode payload (add padding if needed)
        payload_b64 = parts[1]
        # Add padding if needed
        payload_b64 += '=' * (4 - len(payload_b64) % 4)
        payload_json = base64.b64decode(payload_b64)
        payload_data = json.loads(payload_json)

        # Verify no sensitive data in token
        assert "password" not in payload_data
        assert "hashed_password" not in payload_data
        assert "secret" not in str(payload_data).lower()

        # Should contain expected user data
        assert payload_data["sub"] == "test@example.com"
        assert payload_data["user_id"] == 123
        assert "exp" in payload_data  # Expiration time

    def test_password_validation_edge_cases(self):
        """Test password validation with edge cases"""
        edge_cases = [
            "",                        # Empty
            " " * 10,                 # Only spaces
            "12345678",               # Only numbers
            "abcdefgh",               # Only lowercase
            "ABCDEFGH",               # Only uppercase
            "!@#$%^&*",               # Only special chars
            "aA1!",                   # Too short but has all types
            "a" * 100 + "A1!",        # Very long but valid
        ]

        for password in edge_cases[:-1]:  # All should be invalid except last
            assert validate_password_strength(password) is False, f"Password '{password}' should be invalid"

        # Last one should be valid (very long but has all requirements)
        assert validate_password_strength(edge_cases[-1]) is True
