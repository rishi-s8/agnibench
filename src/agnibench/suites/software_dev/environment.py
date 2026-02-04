"""
Simulated environment for the software development benchmark suite.

Provides a simulated codebase with files, errors, tests, and documentation.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from agnibench.core.environment import SimulatedEnvironment
from agnibench.suites.software_dev.tools import set_software_dev_data, get_software_dev_data


class SoftwareDevEnvironment(SimulatedEnvironment):
    """
    Environment for software development tasks.

    Manages a simulated codebase with source files, tests, logs, and documentation.
    """

    def _setup_default_state(self) -> None:
        """Set up default state with sample codebase data."""
        now = datetime.now()

        # Sample source files
        source_files = [
            {
                "id": "file_001",
                "path": "src/auth/user_service.py",
                "language": "python",
                "lines": 156,
                "content": '''"""User authentication service."""
import hashlib
import secrets
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from .models import User, Session
from .database import get_db_connection
from .cache import cache_get, cache_set
from .exceptions import AuthenticationError, UserNotFoundError


class UserService:
    """Handles user authentication and session management."""

    def __init__(self, db_url: str, cache_ttl: int = 3600):
        self.db = get_db_connection(db_url)
        self.cache_ttl = cache_ttl
        self._session_store = {}

    def authenticate(self, username: str, password: str) -> Optional[Session]:
        """Authenticate user and create session.

        Args:
            username: User's username
            password: User's password

        Returns:
            Session object if successful, None otherwise

        Raises:
            AuthenticationError: If credentials are invalid
        """
        user = self._get_user(username)
        if not user:
            raise UserNotFoundError(f"User {username} not found")

        # BUG: Password hash comparison is case-insensitive (security vulnerability)
        stored_hash = user.password_hash.lower()
        provided_hash = self._hash_password(password).lower()

        if stored_hash != provided_hash:
            raise AuthenticationError("Invalid credentials")

        session = self._create_session(user)
        return session

    def _get_user(self, username: str) -> Optional[User]:
        """Retrieve user from cache or database."""
        cache_key = f"user:{username}"
        cached = cache_get(cache_key)
        if cached:
            return User.from_dict(cached)

        user_data = self.db.query("SELECT * FROM users WHERE username = ?", (username,))
        if user_data:
            user = User.from_dict(user_data[0])
            cache_set(cache_key, user.to_dict(), ttl=self.cache_ttl)
            return user
        return None

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def _create_session(self, user: User) -> Session:
        """Create a new session for authenticated user."""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=24)

        session = Session(
            user_id=user.id,
            token=token,
            expires_at=expires_at,
            created_at=datetime.now()
        )

        # BUG: Session not being persisted to database, only stored in memory
        self._session_store[token] = session
        return session

    def validate_session(self, token: str) -> Optional[User]:
        """Validate session token and return user."""
        session = self._session_store.get(token)
        if not session:
            return None

        if session.expires_at < datetime.now():
            del self._session_store[token]
            return None

        return self._get_user_by_id(session.user_id)

    def _get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        user_data = self.db.query("SELECT * FROM users WHERE id = ?", (user_id,))
        if user_data:
            return User.from_dict(user_data[0])
        return None

    def logout(self, token: str) -> bool:
        """Invalidate session."""
        if token in self._session_store:
            del self._session_store[token]
            return True
        return False
''',
                "last_modified": (now - timedelta(days=5)).isoformat(),
                "imports": ["hashlib", "secrets", "typing", "datetime", ".models", ".database", ".cache", ".exceptions"],
                "classes": ["UserService"],
                "functions": ["authenticate", "_get_user", "_hash_password", "_create_session", "validate_session", "_get_user_by_id", "logout"],
                "has_bugs": True,
                "bug_description": "Two bugs: 1) Password hash comparison is case-insensitive (line 42), 2) Sessions not persisted to database (line 73)",
            },
            {
                "id": "file_002",
                "path": "src/auth/models.py",
                "language": "python",
                "lines": 78,
                "content": '''"""Data models for authentication."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class User:
    """User model."""
    id: int
    username: str
    email: str
    password_hash: str
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    role: str = "user"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """Create User from dictionary."""
        return cls(
            id=data["id"],
            username=data["username"],
            email=data["email"],
            password_hash=data["password_hash"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_login=datetime.fromisoformat(data["last_login"]) if data.get("last_login") else None,
            is_active=data.get("is_active", True),
            role=data.get("role", "user"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "is_active": self.is_active,
            "role": self.role,
        }


@dataclass
class Session:
    """Session model."""
    user_id: int
    token: str
    expires_at: datetime
    created_at: datetime = field(default_factory=datetime.now)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.now() > self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "token": self.token,
            "expires_at": self.expires_at.isoformat(),
            "created_at": self.created_at.isoformat(),
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
        }
''',
                "last_modified": (now - timedelta(days=10)).isoformat(),
                "imports": ["dataclasses", "datetime", "typing"],
                "classes": ["User", "Session"],
                "functions": ["from_dict", "to_dict", "is_expired"],
                "has_bugs": False,
            },
            {
                "id": "file_003",
                "path": "src/api/endpoints.py",
                "language": "python",
                "lines": 124,
                "content": '''"""API endpoints for the application."""
from flask import Flask, request, jsonify
from typing import Dict, Any
from ..auth.user_service import UserService
from ..auth.exceptions import AuthenticationError, UserNotFoundError
from .validators import validate_login_request, validate_registration
from .rate_limiter import RateLimiter


app = Flask(__name__)
user_service = UserService(db_url="postgresql://localhost/myapp")
rate_limiter = RateLimiter(max_requests=100, window_seconds=60)


@app.route("/api/login", methods=["POST"])
def login():
    """Handle user login."""
    if not rate_limiter.allow_request(request.remote_addr):
        return jsonify({"error": "Rate limit exceeded"}), 429

    data = request.get_json()
    errors = validate_login_request(data)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        session = user_service.authenticate(data["username"], data["password"])
        return jsonify({
            "token": session.token,
            "expires_at": session.expires_at.isoformat()
        }), 200
    except UserNotFoundError:
        return jsonify({"error": "Invalid credentials"}), 401
    except AuthenticationError:
        return jsonify({"error": "Invalid credentials"}), 401


@app.route("/api/logout", methods=["POST"])
def logout():
    """Handle user logout."""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        return jsonify({"error": "No token provided"}), 401

    # BUG: Missing token validation before logout
    user_service.logout(token)
    return jsonify({"message": "Logged out successfully"}), 200


@app.route("/api/profile", methods=["GET"])
def get_profile():
    """Get user profile."""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        return jsonify({"error": "No token provided"}), 401

    user = user_service.validate_session(token)
    if not user:
        return jsonify({"error": "Invalid or expired session"}), 401

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
    }), 200


@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id: int):
    """Get user by ID (admin only)."""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        return jsonify({"error": "No token provided"}), 401

    current_user = user_service.validate_session(token)
    if not current_user:
        return jsonify({"error": "Invalid or expired session"}), 401

    # BUG: Authorization check is incorrect - should be == "admin", not != "user"
    if current_user.role != "user":
        return jsonify({"error": "Unauthorized"}), 403

    user = user_service._get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
    }), 200
''',
                "last_modified": (now - timedelta(days=2)).isoformat(),
                "imports": ["flask", "typing", "..auth.user_service", "..auth.exceptions", ".validators", ".rate_limiter"],
                "classes": [],
                "functions": ["login", "logout", "get_profile", "get_user"],
                "has_bugs": True,
                "bug_description": "Two bugs: 1) Missing token validation in logout (line 44), 2) Incorrect authorization check in get_user (line 72)",
            },
            {
                "id": "file_004",
                "path": "src/data/repository.py",
                "language": "python",
                "lines": 89,
                "content": '''"""Data repository pattern implementation."""
from typing import List, Optional, Dict, Any, TypeVar, Generic
from abc import ABC, abstractmethod
from datetime import datetime


T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository."""

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[T]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def find_all(self) -> List[T]:
        """Find all entities."""
        pass

    @abstractmethod
    def save(self, entity: T) -> T:
        """Save entity."""
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete entity by ID."""
        pass


class UserRepository(BaseRepository):
    """Repository for User entities."""

    def __init__(self, db_connection):
        self.db = db_connection
        self._cache: Dict[int, Any] = {}

    def find_by_id(self, id: int) -> Optional[Dict[str, Any]]:
        """Find user by ID with caching."""
        if id in self._cache:
            return self._cache[id]

        result = self.db.query("SELECT * FROM users WHERE id = ?", (id,))
        if result:
            self._cache[id] = result[0]
            return result[0]
        return None

    def find_all(self) -> List[Dict[str, Any]]:
        """Find all users."""
        return self.db.query("SELECT * FROM users")

    def find_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Find user by username."""
        result = self.db.query(
            "SELECT * FROM users WHERE username = ?", (username,)
        )
        return result[0] if result else None

    def save(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Save user to database."""
        if "id" in user and user["id"]:
            # Update existing
            self.db.execute(
                "UPDATE users SET username=?, email=?, password_hash=? WHERE id=?",
                (user["username"], user["email"], user["password_hash"], user["id"])
            )
            # BUG: Cache not invalidated after update
        else:
            # Insert new
            user["id"] = self.db.execute(
                "INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
                (user["username"], user["email"], user["password_hash"], datetime.now().isoformat())
            )
            self._cache[user["id"]] = user
        return user

    def delete(self, id: int) -> bool:
        """Delete user by ID."""
        if id in self._cache:
            del self._cache[id]
        result = self.db.execute("DELETE FROM users WHERE id = ?", (id,))
        return result > 0
''',
                "last_modified": (now - timedelta(days=7)).isoformat(),
                "imports": ["typing", "abc", "datetime"],
                "classes": ["BaseRepository", "UserRepository"],
                "functions": ["find_by_id", "find_all", "save", "delete", "find_by_username"],
                "has_bugs": True,
                "bug_description": "Cache not invalidated after user update (line 64)",
            },
            {
                "id": "file_005",
                "path": "src/utils/validators.py",
                "language": "python",
                "lines": 67,
                "content": '''"""Input validation utilities."""
import re
from typing import List, Dict, Any, Optional


def validate_email(email: str) -> Optional[str]:
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return "Invalid email format"
    return None


def validate_password(password: str) -> List[str]:
    """Validate password strength."""
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters")
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain uppercase letter")
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain lowercase letter")
    if not re.search(r"\\d", password):
        errors.append("Password must contain a digit")
    return errors


def validate_username(username: str) -> Optional[str]:
    """Validate username format."""
    if len(username) < 3:
        return "Username must be at least 3 characters"
    if len(username) > 30:
        return "Username must not exceed 30 characters"
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return "Username can only contain letters, numbers, and underscores"
    return None


def validate_login_request(data: Dict[str, Any]) -> List[str]:
    """Validate login request data."""
    errors = []
    if not data:
        return ["Request body is required"]

    if "username" not in data or not data["username"]:
        errors.append("Username is required")
    if "password" not in data or not data["password"]:
        errors.append("Password is required")

    return errors


def validate_registration(data: Dict[str, Any]) -> List[str]:
    """Validate registration request data."""
    errors = []
    if not data:
        return ["Request body is required"]

    if "username" in data:
        username_error = validate_username(data["username"])
        if username_error:
            errors.append(username_error)
    else:
        errors.append("Username is required")

    if "email" in data:
        email_error = validate_email(data["email"])
        if email_error:
            errors.append(email_error)
    else:
        errors.append("Email is required")

    if "password" in data:
        password_errors = validate_password(data["password"])
        errors.extend(password_errors)
    else:
        errors.append("Password is required")

    return errors
''',
                "last_modified": (now - timedelta(days=15)).isoformat(),
                "imports": ["re", "typing"],
                "classes": [],
                "functions": ["validate_email", "validate_password", "validate_username", "validate_login_request", "validate_registration"],
                "has_bugs": False,
            },
            {
                "id": "file_006",
                "path": "tests/test_user_service.py",
                "language": "python",
                "lines": 98,
                "content": '''"""Tests for UserService."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from src.auth.user_service import UserService
from src.auth.models import User, Session
from src.auth.exceptions import AuthenticationError, UserNotFoundError


@pytest.fixture
def mock_db():
    """Create mock database connection."""
    db = Mock()
    db.query.return_value = [{
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "password_hash": "5e884898da28047d9164154d3c1a2a6e0e9d4f5a9b8e7f6c5d4e3f2a1b0c9d8e",  # "password"
        "created_at": datetime.now().isoformat(),
        "is_active": True,
        "role": "user",
    }]
    return db


@pytest.fixture
def user_service(mock_db):
    """Create UserService with mock database."""
    with patch("src.auth.user_service.get_db_connection", return_value=mock_db):
        return UserService(db_url="mock://db")


class TestAuthenticate:
    """Tests for authenticate method."""

    def test_authenticate_valid_credentials(self, user_service, mock_db):
        """Test authentication with valid credentials."""
        with patch("src.auth.user_service.cache_get", return_value=None):
            with patch("src.auth.user_service.cache_set"):
                session = user_service.authenticate("testuser", "password")

        assert session is not None
        assert session.user_id == 1
        assert session.token is not None

    def test_authenticate_invalid_password(self, user_service):
        """Test authentication with invalid password."""
        with patch("src.auth.user_service.cache_get", return_value=None):
            with patch("src.auth.user_service.cache_set"):
                with pytest.raises(AuthenticationError):
                    user_service.authenticate("testuser", "wrongpassword")

    def test_authenticate_user_not_found(self, user_service, mock_db):
        """Test authentication with non-existent user."""
        mock_db.query.return_value = []

        with patch("src.auth.user_service.cache_get", return_value=None):
            with pytest.raises(UserNotFoundError):
                user_service.authenticate("nonexistent", "password")


class TestValidateSession:
    """Tests for validate_session method."""

    def test_validate_valid_session(self, user_service):
        """Test validation of valid session."""
        # Create a session first
        with patch("src.auth.user_service.cache_get", return_value=None):
            with patch("src.auth.user_service.cache_set"):
                session = user_service.authenticate("testuser", "password")

        # Validate it
        user = user_service.validate_session(session.token)
        assert user is not None
        assert user.username == "testuser"

    def test_validate_invalid_token(self, user_service):
        """Test validation of invalid token."""
        user = user_service.validate_session("invalid_token")
        assert user is None

    def test_validate_expired_session(self, user_service):
        """Test validation of expired session."""
        # Create and manually expire session
        with patch("src.auth.user_service.cache_get", return_value=None):
            with patch("src.auth.user_service.cache_set"):
                session = user_service.authenticate("testuser", "password")

        # Manually expire
        session.expires_at = datetime.now() - timedelta(hours=1)
        user_service._session_store[session.token] = session

        user = user_service.validate_session(session.token)
        assert user is None


class TestLogout:
    """Tests for logout method."""

    def test_logout_valid_session(self, user_service):
        """Test logout with valid session."""
        with patch("src.auth.user_service.cache_get", return_value=None):
            with patch("src.auth.user_service.cache_set"):
                session = user_service.authenticate("testuser", "password")

        result = user_service.logout(session.token)
        assert result is True
        assert session.token not in user_service._session_store

    def test_logout_invalid_token(self, user_service):
        """Test logout with invalid token."""
        result = user_service.logout("invalid_token")
        assert result is False
''',
                "last_modified": (now - timedelta(days=3)).isoformat(),
                "imports": ["pytest", "datetime", "unittest.mock", "src.auth.user_service", "src.auth.models", "src.auth.exceptions"],
                "classes": ["TestAuthenticate", "TestValidateSession", "TestLogout"],
                "functions": [],
                "test_file": True,
            },
        ]

        # Error logs
        error_logs = [
            {
                "id": "log_001",
                "timestamp": (now - timedelta(hours=2)).isoformat(),
                "level": "ERROR",
                "file": "src/auth/user_service.py",
                "line": 73,
                "message": "Session persistence failed: sessions lost after server restart",
                "stack_trace": '''Traceback (most recent call last):
  File "src/auth/user_service.py", line 73, in _create_session
    self._session_store[token] = session
RuntimeError: Sessions not persisted to database
''',
                "context": {
                    "user_id": 42,
                    "token_prefix": "eyJ...",
                },
            },
            {
                "id": "log_002",
                "timestamp": (now - timedelta(hours=5)).isoformat(),
                "level": "ERROR",
                "file": "src/api/endpoints.py",
                "line": 72,
                "message": "Unauthorized access: admin user denied access to /api/users/5",
                "stack_trace": '''Traceback (most recent call last):
  File "src/api/endpoints.py", line 72, in get_user
    if current_user.role != "user":
        return jsonify({"error": "Unauthorized"}), 403
''',
                "context": {
                    "user_id": 1,
                    "user_role": "admin",
                    "target_user_id": 5,
                },
            },
            {
                "id": "log_003",
                "timestamp": (now - timedelta(days=1)).isoformat(),
                "level": "WARNING",
                "file": "src/data/repository.py",
                "line": 47,
                "message": "Cache returning stale data for user 15",
                "stack_trace": None,
                "context": {
                    "user_id": 15,
                    "cache_age_seconds": 7200,
                },
            },
            {
                "id": "log_004",
                "timestamp": (now - timedelta(hours=1)).isoformat(),
                "level": "ERROR",
                "file": "src/auth/user_service.py",
                "line": 42,
                "message": "Password hash mismatch: case sensitivity issue suspected",
                "stack_trace": '''Traceback (most recent call last):
  File "src/auth/user_service.py", line 42, in authenticate
    if stored_hash != provided_hash:
        raise AuthenticationError("Invalid credentials")
AuthenticationError: Invalid credentials
''',
                "context": {
                    "username": "JohnDoe",
                    "stored_hash_sample": "A1B2C3...",
                    "provided_hash_sample": "a1b2c3...",
                },
            },
        ]

        # Test results
        test_results = [
            {
                "id": "test_001",
                "file": "tests/test_user_service.py",
                "test_name": "TestAuthenticate::test_authenticate_valid_credentials",
                "status": "passed",
                "duration_ms": 45,
                "timestamp": (now - timedelta(hours=1)).isoformat(),
            },
            {
                "id": "test_002",
                "file": "tests/test_user_service.py",
                "test_name": "TestAuthenticate::test_authenticate_invalid_password",
                "status": "failed",
                "duration_ms": 23,
                "timestamp": (now - timedelta(hours=1)).isoformat(),
                "error_message": "AssertionError: Expected AuthenticationError but got None",
                "failure_reason": "Password comparison is case-insensitive, allowing 'PASSWORD' when 'password' is expected",
            },
            {
                "id": "test_003",
                "file": "tests/test_user_service.py",
                "test_name": "TestValidateSession::test_validate_valid_session",
                "status": "passed",
                "duration_ms": 38,
                "timestamp": (now - timedelta(hours=1)).isoformat(),
            },
            {
                "id": "test_004",
                "file": "tests/test_user_service.py",
                "test_name": "TestValidateSession::test_validate_expired_session",
                "status": "passed",
                "duration_ms": 41,
                "timestamp": (now - timedelta(hours=1)).isoformat(),
            },
            {
                "id": "test_005",
                "file": "tests/test_api_endpoints.py",
                "test_name": "TestGetUser::test_admin_can_access_user",
                "status": "failed",
                "duration_ms": 56,
                "timestamp": (now - timedelta(hours=1)).isoformat(),
                "error_message": "AssertionError: Expected 200, got 403",
                "failure_reason": "Authorization check logic is inverted",
            },
        ]

        # Git history
        git_history = [
            {
                "id": "commit_001",
                "hash": "a1b2c3d4",
                "author": "alice@company.com",
                "message": "Add user authentication service",
                "timestamp": (now - timedelta(days=10)).isoformat(),
                "files_changed": ["src/auth/user_service.py", "src/auth/models.py"],
            },
            {
                "id": "commit_002",
                "hash": "e5f6g7h8",
                "author": "bob@company.com",
                "message": "Implement API endpoints for login/logout",
                "timestamp": (now - timedelta(days=7)).isoformat(),
                "files_changed": ["src/api/endpoints.py", "src/api/validators.py"],
            },
            {
                "id": "commit_003",
                "hash": "i9j0k1l2",
                "author": "alice@company.com",
                "message": "Add caching to user repository",
                "timestamp": (now - timedelta(days=5)).isoformat(),
                "files_changed": ["src/data/repository.py"],
            },
            {
                "id": "commit_004",
                "hash": "m3n4o5p6",
                "author": "carol@company.com",
                "message": "Add rate limiting to login endpoint",
                "timestamp": (now - timedelta(days=3)).isoformat(),
                "files_changed": ["src/api/endpoints.py", "src/api/rate_limiter.py"],
            },
            {
                "id": "commit_005",
                "hash": "q7r8s9t0",
                "author": "bob@company.com",
                "message": "Optimize password hashing (converted to lowercase for consistency)",
                "timestamp": (now - timedelta(days=2)).isoformat(),
                "files_changed": ["src/auth/user_service.py"],
            },
        ]

        # Documentation
        documentation = [
            {
                "id": "doc_001",
                "title": "Authentication System Overview",
                "path": "docs/auth/overview.md",
                "content": """# Authentication System

## Overview
The authentication system handles user login, session management, and authorization.

## Components
- **UserService**: Core authentication logic
- **Session**: JWT-like token-based sessions
- **Rate Limiter**: Prevents brute-force attacks

## Security Features
- Password hashing with SHA-256
- Session expiration after 24 hours
- Rate limiting on login endpoint

## Known Issues
- Sessions are not persisted to database (in-memory only)
- Need to implement refresh tokens
""",
                "last_updated": (now - timedelta(days=5)).isoformat(),
            },
            {
                "id": "doc_002",
                "title": "API Reference",
                "path": "docs/api/reference.md",
                "content": """# API Reference

## Authentication Endpoints

### POST /api/login
Login with username and password.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "token": "string",
  "expires_at": "ISO datetime"
}
```

### POST /api/logout
Logout current session.

**Headers:**
- Authorization: Bearer {token}

### GET /api/profile
Get current user profile.

### GET /api/users/{id}
Get user by ID (admin only).
""",
                "last_updated": (now - timedelta(days=3)).isoformat(),
            },
        ]

        # Set state
        self.state = {
            "source_files": source_files,
            "error_logs": error_logs,
            "test_results": test_results,
            "git_history": git_history,
            "documentation": documentation,
            # Tracking state changes
            "fixes_applied": [],
            "tests_run": [],
            "notes_added": [],
        }

        # Also set the data in the tools module
        set_software_dev_data(self.state)

    def get_state(self) -> Dict[str, Any]:
        """Get current environment state."""
        return self.state

    def reset_state(self) -> None:
        """Reset environment to default state."""
        self._setup_default_state()
