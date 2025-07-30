"""
Example usage of alchemy-h8: A comprehensive SQLAlchemy-based database library

This example demonstrates key features:
1. Connection configuration and setup
2. Rate limiting with different strategies
3. Connection pooling with security features
4. Read/write splitting using replicas
5. Error handling and retries
6. Creating and using repositories
"""

import asyncio
import logging
from datetime import datetime
from typing import Generic, List, Optional, TypeVar
from uuid import UUID, uuid4

import structlog
from pydantic import PostgresDsn
from sqlalchemy import Column, ForeignKey, String, select, text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

from src.alchemy_h8.config import DBConnectionConfig, RateLimiterStrategy
from src.alchemy_h8.connection import DBConnectionHandler
from src.alchemy_h8.rate_limiter import RateLimiterError

# Set up structured logging
structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)
logger = structlog.get_logger()

base = declarative_base()
# Define database models


class BaseModel(base):
    """Base model for all models."""

    __abstract__ = True

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)


T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Base repository for all repositories."""

    model_class: T
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, model: T) -> T:
        """Create a new model."""
        self.session.add(model)
        await self.session.commit()
        return model


# Define example models
class User(BaseModel):
    """Example user model."""

    __tablename__ = "users"

    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"User(id={self.id}, name='{self.name}', email='{self.email}')"


class Post(BaseModel):
    """Example post model linked to a user."""

    __tablename__ = "posts"

    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    def __repr__(self) -> str:
        return f"Post(id={self.id}, title='{self.title}', user_id={self.user_id})"


# Define repositories
class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""

    model_class = User

    async def get_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        query = select(self.model_class).where(self.model_class.email == email)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_all_users(self) -> List[User]:
        """Get all users."""
        query = select(self.model_class)
        result = await self.session.execute(query)
        return list(result.scalars().all())


class PostRepository(BaseRepository[Post]):
    """Repository for Post model operations."""

    model_class = Post

    async def get_by_user_id(self, user_id: UUID) -> List[Post]:
        """Find posts by user_id."""
        query = select(self.model_class).where(self.model_class.user_id == user_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())


# Example DB operations
async def create_sample_data(session: AsyncSession) -> None:
    """Create sample data in the database."""
    # Create repositories
    user_repo = UserRepository(session)
    post_repo = PostRepository(session)

    # Create users
    user1 = User(id=uuid4(), name="Alice Smith", email="alice@example.com")
    user2 = User(id=uuid4(), name="Bob Johnson", email="bob@example.com")

    # Save users
    await user_repo.create(user1)
    await user_repo.create(user2)
    logger.info("Created users", count=2)

    # Create posts
    post1 = Post(
        id=uuid4(),
        title="First Post",
        content="This is Alice's first post!",
        user_id=user1.id,
    )
    post2 = Post(id=uuid4(), title="Welcome", content="Bob's introduction post", user_id=user2.id)
    post3 = Post(
        id=uuid4(),
        title="Another post",
        content="Alice's second post",
        user_id=user1.id,
    )

    # Save posts
    await post_repo.create(post1)
    await post_repo.create(post2)
    await post_repo.create(post3)
    logger.info("Created posts", count=3)


async def read_data(session: AsyncSession) -> None:
    """Read data using repositories."""
    # Create repositories
    user_repo = UserRepository(session)
    post_repo = PostRepository(session)

    # Find users
    users = await user_repo.get_all_users()
    logger.info("Retrieved users", count=len(users))

    # Find posts for each user
    for user in users:
        posts = await post_repo.get_by_user_id(user.id)
        logger.info("User posts", user_name=user.name, post_count=len(posts))
        for post in posts:
            logger.info("Post", title=post.title, content=post.content[:20] + "...")


async def create_tables(db_handler: DBConnectionHandler) -> None:
    """Create database tables."""
    async with db_handler.get_async_connection() as conn:
        # Create tables
        await conn.run_sync(BaseModel.metadata.create_all)
        await conn.commit()
        logger.info("Created database tables")


async def demonstrate_rate_limiting(db_handler: DBConnectionHandler) -> None:
    """Demonstrate rate limiting by making many requests in parallel."""
    logger.info("Demonstrating rate limiting...")

    async def execute_query(i: int) -> None:
        try:
            async with db_handler.async_session_scope() as conn:
                await conn.execute(text("SELECT pg_sleep(0.1)"))
                logger.info(f"Query {i} completed successfully")
        except RateLimiterError as e:
            logger.warning(f"Query {i} rate limited: {str(e)}")
        except Exception as e:
            logger.error(f"Query {i} failed: {str(e)}")

    # Create many concurrent tasks to trigger rate limiting
    tasks = [execute_query(i) for i in range(100)]
    await asyncio.gather(*tasks)


async def demonstrate_read_replicas(db_handler: DBConnectionHandler) -> None:
    """Demonstrate read replica distribution."""
    logger.info("Demonstrating read replica distribution...")

    async def read_query(i: int) -> None:
        async with db_handler.async_session_scope(read_only=True) as session:
            user_repo = UserRepository(session)
            await user_repo.get_all_users()

    # Run concurrent read queries to see read replica distribution
    tasks = [read_query(i) for i in range(20)]
    await asyncio.gather(*tasks)


async def main() -> None:
    """Main function demonstrating all features."""
    # Create primary database connection configuration
    primary_db_url = PostgresDsn.build(
        scheme="postgresql+asyncpg",
        host="localhost",
        port=5432,
        username="postgres",
        password="postgres",  # nosec
        path="test_db",
    )

    # Create read replica configuration (same DB for demo purposes)
    # In production, these would be separate database servers
    replica1_url = PostgresDsn.build(
        scheme="postgresql+asyncpg",
        host="localhost",
        port=5432,
        username="postgres",
        password="postgres",  # nosec
        path="test_db",
    )

    replica2_url = PostgresDsn.build(
        scheme="postgresql+asyncpg",
        host="localhost",
        port=5432,
        username="postgres",
        password="postgres",  # nosec
        path="test_db",
    )

    # Configure the database connection with advanced features
    config = DBConnectionConfig(
        url=primary_db_url,
        # Connection pooling settings
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,  # 30 minutes
        # Enable read replicas
        read_replica_hosts=[replica1_url, replica2_url],
        use_read_replicas_for_reads=True,
        # Rate limiting settings
        use_rate_limiter=True,
        rate_limit_max_requests=30,  # Allow 30 requests per 5 second window
        rate_limit_time_window=5,
        rate_limit_strategy=RateLimiterStrategy.TOKEN_BUCKET,
        idle_connection_timeout=300,  # 5 minutes
        # Retry configuration
        max_retries=3,
        base_retry_delay=1,
        max_retry_delay=5,
        retry_jitter=0.1,
        retry_backoff=2,
        # Circuit breaker settings
        use_circuit_breaker=True,
        circuit_breaker_threshold=5,
        circuit_breaker_recovery_timeout=30,
    )

    # Create and initialize DB handler
    start_time = datetime.now()
    logger.info("Initializing database connection")
    db_handler = DBConnectionHandler(config)
    await db_handler.initialize()

    try:
        # Create tables if they don't exist
        await create_tables(db_handler)

        # Create sample data
        logger.info("Creating sample data")
        async with db_handler.async_session_scope() as session:
            await create_sample_data(session)

        # Read data using read replicas
        logger.info("Reading data using read replicas")
        await demonstrate_read_replicas(db_handler)

        # Demonstrate rate limiting
        logger.info("Testing rate limiting")
        await demonstrate_rate_limiting(db_handler)

        # Read data to confirm everything still works
        logger.info("Reading data again")
        async with db_handler.async_session_scope(read_only=True) as session:
            await read_data(session)

    except Exception as e:
        logger.error(f"Error during execution: {str(e)}")
    finally:
        # Clean up resources
        await db_handler.dispose_gracefully()
        execution_time = datetime.now() - start_time
        logger.info(f"Example completed in {execution_time.total_seconds():.2f} seconds")


# Run the example
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Example interrupted by user")
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
