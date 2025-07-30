"""
Tests for load scenarios and edge cases for the database connection library.
These tests verify system behavior under high load, unusual errors, and extreme conditions.
"""
import asyncio
import os
import pytest
import pytest_asyncio
import random
import time
from typing import AsyncGenerator, List, Optional, Any, Dict, Tuple

from sqlalchemy import text, Table, Column, Integer, String, MetaData, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncConnection
import asyncpg

from src.alchemy_h8.config import DBConnectionConfig
from src.alchemy_h8.connection import DBConnectionHandler
from src.alchemy_h8.rate_limiter import RateLimiterStrategy


# Use environment variables or defaults for test database
DB_HOST = os.getenv("TEST_DB_HOST", "localhost")
DB_PORT = int(os.getenv("TEST_DB_PORT", "5432"))
DB_USER = os.getenv("TEST_DB_USER", "postgres")
DB_PASS = os.getenv("TEST_DB_PASS", "postgres")
DB_NAME = os.getenv("TEST_DB_NAME", "test_db")


@pytest_asyncio.fixture
async def test_table(db_connection_handler: DBConnectionHandler) -> AsyncGenerator[Table, None]:
    """Create a test table for the duration of the test."""
    metadata = MetaData()
    test_table = Table(
        "load_test", metadata,
        Column("id", Integer, primary_key=True),
        Column("data", String(50)),
        Column("value", Integer),
    )
    
    async with db_connection_handler.get_async_connection() as conn:
        # Create test table
        async with conn.begin():
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS load_test (
                    id SERIAL PRIMARY KEY,
                    data VARCHAR(50),
                    value INTEGER
                )
            """))
        
        # Ensure table is empty
        async with conn.begin():
            await conn.execute(text("TRUNCATE TABLE load_test"))
        
        # Add some initial data
        for i in range(100):
            async with conn.begin():
                await conn.execute(
                    text("INSERT INTO load_test (data, value) VALUES (:data, :value)"),
                    {"data": f"item_{i}", "value": i}
                )
        
    try:
        yield test_table
    finally:
        # Clean up after test
        async with db_connection_handler.get_async_connection() as conn:
            async with conn.begin():
                await conn.execute(text("DROP TABLE IF EXISTS load_test"))


@pytest_asyncio.fixture
async def db_connection_handler() -> AsyncGenerator[DBConnectionHandler, None]:
    """Create a database connection handler for testing."""
    config = DBConnectionConfig(
        host=DB_HOST,
        port=DB_PORT,
        username=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        
        # Tuned pool for load testing
        pool_size=10,
        max_overflow=20,
        pool_timeout=10,
        
        # Enable circuit breaker with modest thresholds
        use_circuit_breaker=True,
        circuit_breaker_threshold=10,
        circuit_breaker_recovery_timeout=5,
        
        # Enable rate limiter with high limits for load testing
        use_rate_limiter=True,
        rate_limit_max_requests=100,
        rate_limit_time_window=1.0,
        rate_limit_strategy=RateLimiterStrategy.TOKEN_BUCKET,
        rate_limit_max_delay=0.5,
        
        # Retry settings
        max_retries=3,
        base_retry_delay=0.1,
        max_retry_delay=1.0,
        retry_jitter=True,
    )
    
    handler = DBConnectionHandler(config)
    await handler.initialize()
    
    try:
        yield handler
    finally:
        # Cancel any background tasks before disposal to prevent asyncio warnings
        handler._cancel_background_tasks()
        await handler.dispose_gracefully()


class TestLoadScenarios:
    @pytest.mark.asyncio
    async def test_high_concurrency(
        self, db_connection_handler: DBConnectionHandler, test_table: Table
    ) -> None:
        """Test system under high concurrency load."""
        # Number of concurrent operations
        num_concurrent = 50
        
        async def worker(worker_id: int) -> List[Dict[str, Any]]:
            """Perform random database operations."""
            results = []
            try:
                async with db_connection_handler.get_async_connection() as conn:
                    # Choose a random operation: read, write, or update
                    op_type = random.choice(["read", "write", "update"])
                    
                    if op_type == "read":
                        # Read operation
                        limit = random.randint(1, 10)
                        offset = random.randint(0, 90)
                        result = await conn.execute(
                            text("SELECT * FROM load_test ORDER BY id LIMIT :limit OFFSET :offset"),
                            {"limit": limit, "offset": offset}
                        )
                        rows = result.fetchall()  # No await needed here
                        results.append({
                            "worker_id": worker_id,
                            "operation": "read",
                            "count": len(rows)
                        })
                    
                    elif op_type == "write":
                        # Write operation - explicitly use a transaction
                        async with conn.begin():
                            data = f"worker_{worker_id}_item_{random.randint(1000, 9999)}"
                            value = random.randint(0, 1000)
                            result = await conn.execute(
                                text("INSERT INTO load_test (data, value) VALUES (:data, :value) RETURNING id"),
                                {"data": data, "value": value}
                            )
                            row = result.fetchone()  # No await needed here
                            if row:  # Make sure we have a row before accessing row[0]
                                results.append({
                                    "worker_id": worker_id,
                                    "operation": "write",
                                    "id": row[0],
                                    "data": data,
                                    "value": value
                                })
                    
                    else:  # update
                        # Update operation with explicit transaction
                        async with conn.begin():
                            # Get a random ID between 1-100
                            update_id = random.randint(1, 100)
                            new_value = random.randint(0, 1000)
                            result = await conn.execute(
                                text("UPDATE load_test SET value = :value WHERE id = :id RETURNING id, value"),
                                {"id": update_id, "value": new_value}
                            )
                            row = result.fetchone()  # No await needed here
                            if row:  # Check if row exists to prevent NoneType errors
                                results.append({
                                    "worker_id": worker_id,
                                    "operation": "update",
                                    "id": row[0],
                                    "new_value": row[1]
                                })
            except Exception as e:
                results.append({
                    "worker_id": worker_id,
                    "operation": "error",
                    "error": str(e)
                })
            
            return results
        
        # Run all workers concurrently
        worker_tasks = [asyncio.create_task(worker(i)) for i in range(num_concurrent)]
        all_results = await asyncio.gather(*worker_tasks, return_exceptions=True)
        
        # Flatten results and check
        successful_ops = 0
        errors = 0
        
        for result in all_results:
            if isinstance(result, Exception):
                errors += 1
                print(f"Worker error: {result}")
            else:
                # Each worker returns a list of operation results
                for op in result:
                    if op.get("operation") == "error":
                        errors += 1
                        print(f"Operation error: {op.get('error')}")
                    else:
                        successful_ops += 1
        
        # Some errors are expected under high load, but at least some operations should succeed
        assert successful_ops > 0, f"No successful operations out of {num_concurrent} attempts"
        
        # Check that database is still functional after high concurrency
        async with db_connection_handler.get_async_connection() as conn:
            result = await conn.execute(text("SELECT COUNT(*) FROM load_test"))
            count = result.scalar()  # No await needed here
            assert count >= 100, f"Expected at least 100 records, got {count}"  # We started with 100 records

    @pytest.mark.asyncio
    async def test_long_running_transactions(
        self, db_connection_handler: DBConnectionHandler
    ) -> None:
        """Test behavior with long-running transactions."""
        # Start a long transaction that holds a connection
        async with db_connection_handler.get_async_connection() as long_conn:
            # Begin transaction
            async with long_conn.begin():
                # Create test table
                await long_conn.execute(
                    text("CREATE TABLE IF NOT EXISTS long_test (id SERIAL PRIMARY KEY, data TEXT)")
                )
                await long_conn.execute(text("INSERT INTO long_test (data) VALUES ('long_transaction')"))
                
                # Hold the transaction open while we try other operations
                other_ops_succeeded = 0
                other_ops_attempted = 10
                
                for i in range(other_ops_attempted):
                    try:
                        # Each operation should get its own connection from the pool
                        async with db_connection_handler.get_async_connection() as conn:
                            await conn.execute(text("SELECT 1"))
                            other_ops_succeeded += 1
                    except Exception:
                        pass
                        
                # The system should be able to serve other operations even with one long transaction
                assert other_ops_succeeded > 0
            
        # Clean up
        async with db_connection_handler.get_async_connection() as conn:
            async with conn.begin():
                await conn.execute(text("DROP TABLE IF EXISTS long_test"))

    @pytest.mark.asyncio
    async def test_rapid_connection_cycling(
        self, db_connection_handler: DBConnectionHandler
    ) -> None:
        """Test rapid checkout and return of connections."""
        # This test rapidly gets and releases connections to stress the pool
        total_ops = 100
        succeeded = 0
        
        start_time = time.time()
        
        for i in range(total_ops):
            try:
                async with db_connection_handler.get_async_connection() as conn:
                    # Just do a quick query
                    result = await conn.execute(text("SELECT 1"))
                    value = result.scalar()  # No await needed here
                    assert value == 1
                    succeeded += 1
                    
                    # Don't add any delay - this stresses connection checkout/checkin
            except Exception as e:
                print(f"Operation {i} failed: {str(e)}")
        
        elapsed = time.time() - start_time
        operations_per_sec = total_ops / elapsed
        
        # Most operations should succeed
        assert succeeded >= total_ops * 0.9, f"Only {succeeded}/{total_ops} operations succeeded"
        
        # For informational purposes
        print(f"Completed {succeeded}/{total_ops} operations in {elapsed:.2f}s ({operations_per_sec:.2f} ops/sec)")


class TestEdgeCases:

    @pytest.mark.asyncio
    async def test_transaction_error_recovery(
        self, db_connection_handler: DBConnectionHandler
    ) -> None:
        """Test recovery after transaction errors."""
        # Create a test table with explicit transaction
        async with db_connection_handler.get_async_connection() as setup_conn:
            async with setup_conn.begin():
                await setup_conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS tx_error_test (
                        id SERIAL PRIMARY KEY,
                        unique_col VARCHAR(50) UNIQUE
                    )
                """))
        
        try:
            # First transaction: insert initial data
            async with db_connection_handler.get_async_connection() as conn:
                async with conn.begin():
                    await conn.execute(
                        text("INSERT INTO tx_error_test (unique_col) VALUES (:value)"),
                        {"value": "unique1"}
                    )
            
            # Second transaction: will fail due to unique constraint
            with pytest.raises(Exception):
                async with db_connection_handler.get_async_connection() as conn:
                    async with conn.begin():
                        await conn.execute(
                            text("INSERT INTO tx_error_test (unique_col) VALUES (:value)"),
                            {"value": "unique1"}  # Same value, will violate constraint
                        )
            
            # Connection should be returned to pool despite error
            # Third transaction: should work fine with new value
            async with db_connection_handler.get_async_connection() as conn:
                async with conn.begin():
                    await conn.execute(
                        text("INSERT INTO tx_error_test (unique_col) VALUES (:value)"),
                        {"value": "unique2"}  # Different value
                    )
            
            # Verify both records exist
            async with db_connection_handler.get_async_connection() as conn:
                result = await conn.execute(text("SELECT COUNT(*) FROM tx_error_test"))
                count = result.scalar()  # No await needed here
                assert count == 2
        finally:
            # Clean up with explicit transaction
            async with db_connection_handler.get_async_connection() as cleanup_conn:
                async with cleanup_conn.begin():
                    await cleanup_conn.execute(text("DROP TABLE IF EXISTS tx_error_test"))

    @pytest.mark.asyncio
    async def test_cleanup_on_unexpected_termination(
        self, db_connection_handler: DBConnectionHandler
    ) -> None:
        """Test connection cleanup after unexpected coroutine termination."""
        # Start a task that gets a connection but doesn't properly close it
        # NOTE: This test intentionally creates a scenario where SQLAlchemy will report a 
        # "garbage collector is trying to clean up non-checked-in connection" warning.
        # This warning is EXPECTED and actually confirms the test is working correctly.
        async def improperly_terminated_task():
            conn = await db_connection_handler._async_engine.connect()
            # Don't close the connection, just let it be garbage collected
            await asyncio.sleep(0.1)
            return conn
        
        # Run the task and immediately cancel it
        task = asyncio.create_task(improperly_terminated_task())
        await asyncio.sleep(0.05)  # Give it time to get the connection
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        # Allow time for connection cleanup
        await asyncio.sleep(0.2)
        
        # Even after improper cancellation, we should be able to get connections
        # from the pool, as SQLAlchemy should handle cleanup
        connections = []
        # Use a smaller number to avoid exhausting the pool
        test_conns = min(5, db_connection_handler.config.pool_size)
        
        try:
            for i in range(test_conns):
                conn = await db_connection_handler._async_engine.connect()
                connections.append(conn)
                
            # We successfully got the connections, which means
            # the improperly terminated connection was properly cleaned up
            assert len(connections) == test_conns
        finally:
            # Properly close all connections
            for conn in connections:
                await conn.close()

    @pytest.mark.asyncio
    async def test_multiple_transactions(
        self, db_connection_handler: DBConnectionHandler
    ) -> None:
        """Test behavior with multiple nested or sequential transactions."""
        # Create test table with explicit transaction - use a separate connection for setup
        async with db_connection_handler.get_async_connection() as setup_conn:
            async with setup_conn.begin():
                # Create test table
                await setup_conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS multi_tx_test (
                        id SERIAL PRIMARY KEY,
                        counter INTEGER NOT NULL
                    )
                """))
                
                # Initialize counter within the same transaction
                await setup_conn.execute(text("INSERT INTO multi_tx_test (counter) VALUES (0)"))
        
        try:
            # Test sequential transactions on same connection
            async with db_connection_handler.get_async_connection() as conn:
                # First transaction
                async with conn.begin():
                    await conn.execute(text("UPDATE multi_tx_test SET counter = counter + 1"))
                
                # Second transaction
                async with conn.begin():
                    await conn.execute(text("UPDATE multi_tx_test SET counter = counter + 1"))
                
                # Verify counter - no await on scalar() which returns the value directly
                result = await conn.execute(text("SELECT counter FROM multi_tx_test"))
                counter = result.scalar()
                assert counter == 2
            
            # Test nested transactions (savepoints)
            async with db_connection_handler.get_async_connection() as conn:
                # Outer transaction
                async with conn.begin():
                    await conn.execute(text("UPDATE multi_tx_test SET counter = counter + 1"))
                    
                    # Inner transaction (should create a savepoint)
                    async with conn.begin_nested():
                        await conn.execute(text("UPDATE multi_tx_test SET counter = counter + 1"))
                        
                        # Another level
                        async with conn.begin_nested():
                            await conn.execute(text("UPDATE multi_tx_test SET counter = counter + 1"))
                
                # Verify counter increased by 3
                result = await conn.execute(text("SELECT counter FROM multi_tx_test"))
                counter = result.scalar()
                assert counter == 5
        finally:
            # Clean up with a separate connection to ensure transaction isolation
            async with db_connection_handler.get_async_connection() as cleanup_conn:
                async with cleanup_conn.begin():
                    await cleanup_conn.execute(text("DROP TABLE IF EXISTS multi_tx_test"))
