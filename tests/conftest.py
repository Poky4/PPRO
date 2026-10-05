import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.core.database import Base, get_db
from src.domain.models.user import User, UserRole
from src.core.security import get_password_hash, create_access_token

# SQLite v paměti pro rychlé a izolované testy
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session() -> Generator:
    """Vytvoří čistou DB pro každý jednotlivý test."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session) -> Generator:
    """Testovací HTTP klient s přepsanou get_db dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db_session) -> User:
    """Vytvoří testovacího administrátora."""
    user = User(
        username="testadmin",
        email="admin@test.local",
        hashed_password=get_password_hash("adminpass123"),
        full_name="Test Administrátor",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_token_headers(admin_user) -> dict:
    """Vrátí HTTP Authorization header s tokenem administrátora."""
    token = create_access_token(subject=admin_user.username)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def normal_user(db_session) -> User:
    """Vytvoří testovacího běžného uživatele (recepční)."""
    user = User(
        username="testrecepce",
        email="recepce@test.local",
        hashed_password=get_password_hash("recepcepass123"),
        full_name="Paní Věra Testovací",
        role=UserRole.RECEPCNI,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def normal_token_headers(normal_user) -> dict:
    """Vrátí HTTP Authorization header s tokenem recepční."""
    token = create_access_token(subject=normal_user.username)
    return {"Authorization": f"Bearer {token}"}
