"""
Pytest configuration and shared fixtures
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.dependencies import get_db

# Import all models here to register them with Base.metadata
from app.db.models.user import User
from app.db.models.project import Project
from app.db.models.research_paper import ResearchPaper
from app.db.models.paper_chunk import PaperChunk
from app.db.models.analysis_run import AnalysisRun
from app.db.models.contradiction import Contradiction
from app.db.models.research_gap import ResearchGap
from app.db.models.protocol import ExperimentalProtocol
from app.db.models.reasoning_trace import ReasoningTrace
from app.db.models.export import Export
from app.db.models.activity_log import ActivityLog

# Use PostgreSQL for tests (isolated test database)
SQLALCHEMY_TEST_DATABASE_URL = "postgresql://user:onion123@localhost:5432/scoinvestigator_test"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create fresh DB tables for each test, then drop them."""
    # Ensure extensions exist
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS "pgcrypto"'))
        conn.commit()
        
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Clean teardown for PostgreSQL
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("DROP SCHEMA public CASCADE"))
            conn.execute(text("CREATE SCHEMA public"))
            conn.execute(text('GRANT ALL ON SCHEMA public TO public'))
            conn.execute(text('GRANT ALL ON SCHEMA public TO "user"'))
            conn.commit()


@pytest.fixture(scope="function")
def client(db):
    """FastAPI test client with DB override."""
    # Import here to avoid settings validation at import time
    from app.main import app

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
