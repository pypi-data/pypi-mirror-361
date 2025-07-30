"""
Pytest configuration for resilience tests.
Provides common fixtures and setup/teardown for database resilience tests.
"""
import asyncio
import os
import pytest
import logging
import structlog
from typing import Generator, AsyncGenerator, Any, Dict, Optional

import asyncpg
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy import text

# Configure structlog to use simple console output
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

# Configure logging level
logging.basicConfig(level=logging.INFO)
logger = structlog.get_logger()


# Test database settings
TEST_DB_HOST = os.environ.get("TEST_DB_HOST", "localhost")
TEST_DB_PORT = int(os.environ.get("TEST_DB_PORT", "5432"))
TEST_DB_USER = os.environ.get("TEST_DB_USER", "postgres")
TEST_DB_PASS = os.environ.get("TEST_DB_PASS", "postgres")
TEST_DB_NAME = os.environ.get("TEST_DB_NAME", "alchemy_h8_test_db")

# Flag to control whether tests should launch their own test database
USE_DOCKER_DB = os.environ.get("USE_DOCKER_DB", "false").lower() == "true"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db_engine(docker_postgres: Dict[str, Any]) -> AsyncGenerator[AsyncEngine, None]:
    """Create a SQLAlchemy engine connected to the test database."""
    host = docker_postgres["host"]
    port = docker_postgres["port"]
    user = docker_postgres["user"]
    password = docker_postgres["password"]
    database = docker_postgres["database"]
    
    engine = create_async_engine(
        f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}",
        echo=False,
        pool_size=5,
        max_overflow=10
    )
    
    # Initialize test database with any required schemas or extensions
    async with engine.begin() as conn:
        # Create test schema if needed
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS test_schema"))
        
        # Create any extensions if needed
        # await conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))
    
    yield engine
    
    # Close engine after tests
    await engine.dispose()


@pytest.fixture
async def cleanup_tables(test_db_engine: AsyncEngine) -> AsyncGenerator[None, None]:
    """Clean up any test tables after each test."""
    yield
    
    # List of tables to clean up after tests
    test_tables = [
        "resilience_test", 
        "security_test", 
        "validation_test", 
        "load_test",
        "tx_error_test",
        "multi_tx_test",
        "long_test"
    ]
    
    async with test_db_engine.begin() as conn:
        for table in test_tables:
            try:
                await conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
            except Exception as e:
                logger.warning(f"Error dropping table {table}: {str(e)}")
