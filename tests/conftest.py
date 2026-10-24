"""
TITAN Test Suite Configuration & Fixtures
Configures in-memory SQLite isolation, mock database sessions, and FastAPI TestClient.
"""

import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure apps and services are on PYTHONPATH
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(root_dir, "apps", "inventory-api"))
sys.path.insert(0, os.path.join(root_dir, "services", "platform-api"))
sys.path.insert(0, os.path.join(root_dir, "services", "incident-engine"))
sys.path.insert(0, os.path.join(root_dir, "packages", "common-models"))
sys.path.insert(0, os.path.join(root_dir, "packages", "experiment-runner"))
sys.path.insert(0, root_dir)

# Force test environment variables before importing app
os.environ["ENVIRONMENT"] = "testing"
os.environ["ENABLE_FAULT_INJECTION"] = "true"
os.environ["FAULT_INJECTION_AUTH_TOKEN"] = "test-token-xyz"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from inventory_api.database import get_db  # noqa: E402
from inventory_api.main import app  # noqa: E402
from inventory_api.models.item import Base  # noqa: E402

# In-memory SQLite engine for fast, isolated tests
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(name="db_session")
def fixture_db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()


@pytest.fixture(name="client")
def fixture_client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
