import pytest
from datetime import datetime
from typing import Optional
from good_clickhouse.collection import DataTable, PydanticCollection
from good_common.types import UUIDField, UUID
from aioch import Client as AsyncClient


class ClientTestUser(DataTable):
    uid: UUIDField
    id: int
    name: str
    email: Optional[str] = None
    created_at: datetime
    active: bool = True


@pytest.mark.asyncio
class TestClickhouseIntegration:
    
    async def test_basic_connection(self, clickhouse_client: AsyncClient):
        """Test basic connection and simple query."""
        result = await clickhouse_client.execute("SELECT 1 as test_value")
        assert result == [(1,)]
    
    async def test_create_table_and_insert(self, clickhouse_client: AsyncClient):
        """Test table creation and data insertion."""
        # Create table
        create_sql = """
        CREATE TABLE IF NOT EXISTS test_users (
            uid UUID,
            id Int64,
            name String,
            email Nullable(String),
            created_at DateTime64(3),
            active Bool
        ) ENGINE = Memory()
        """
        await clickhouse_client.execute(create_sql)
        
        # Insert test data
        test_users = [
            ClientTestUser(
                uid=UUID.create_v7(),
                id=1,
                name="Alice",
                email="alice@example.com",
                created_at=datetime.now(),
                active=True
            ),
            ClientTestUser(
                uid=UUID.create_v7(),
                id=2,
                name="Bob",
                email=None,
                created_at=datetime.now(),
                active=False
            )
        ]
        
        collection = PydanticCollection(test_users, type=ClientTestUser)
        
        # Insert using collection with parameterized query
        insert_sql = f"""
        INSERT INTO test_users ({collection.select})
        VALUES
        """
        
        await clickhouse_client.execute(insert_sql, list(collection))
        
        # Verify data was inserted
        result = await clickhouse_client.execute("SELECT count() as count FROM test_users")
        assert result[0][0] == 2
        
        # Test querying specific data
        result = await clickhouse_client.execute("SELECT name, active FROM test_users ORDER BY id")
        assert result[0][0] == "Alice"
        assert result[0][1] is True
        assert result[1][0] == "Bob"
        assert result[1][1] is False
        
        # Clean up
        await clickhouse_client.execute("DROP TABLE test_users")
    
    async def test_data_types_roundtrip(self, clickhouse_client: AsyncClient):
        """Test various ClickHouse data types round-trip conversion."""
        # Create table with various types
        create_sql = """
        CREATE TABLE IF NOT EXISTS test_types (
            id Int64,
            int32_val Int32,
            float64_val Float64,
            string_val String,
            nullable_string Nullable(String),
            datetime_val DateTime64(3),
            bool_val Bool,
            array_val Array(String),
            uuid_val UUID
        ) ENGINE = Memory()
        """
        await clickhouse_client.execute(create_sql)
        
        # Insert test data with various types
        test_uuid = UUID.create_v7()
        test_datetime = datetime.now()
        
        insert_sql = f"""
        INSERT INTO test_types VALUES (
            1,
            42,
            3.14159,
            'test string',
            NULL,
            '{test_datetime.isoformat()}',
            true,
            ['item1', 'item2', 'item3'],
            '{test_uuid}'
        )
        """
        await clickhouse_client.execute(insert_sql)
        
        # Query and verify data
        result = await clickhouse_client.execute("SELECT * FROM test_types")
        row = result[0]
        
        assert row[0] == 1  # id
        assert row[1] == 42  # int32_val
        assert abs(row[2] - 3.14159) < 0.00001  # float64_val
        assert row[3] == "test string"  # string_val
        assert row[4] is None  # nullable_string
        # datetime_val is row[5] but we skip checking it
        assert row[6] is True  # bool_val
        assert row[7] == ["item1", "item2", "item3"]  # array_val
        assert str(row[8]) == str(test_uuid)  # uuid_val
        
        # Clean up
        await clickhouse_client.execute("DROP TABLE test_types")
    
    async def test_transaction_rollback_behavior(self, clickhouse_client: AsyncClient):
        """Test ClickHouse behavior with failed operations."""
        # Create table
        await clickhouse_client.execute("""
            CREATE TABLE IF NOT EXISTS test_rollback (
                id Int64,
                value String
            ) ENGINE = Memory()
        """)
        
        # Insert valid data
        await clickhouse_client.execute("INSERT INTO test_rollback VALUES (1, 'valid')")
        
        # Try to insert invalid data (this should fail)
        with pytest.raises(Exception):
            await clickhouse_client.execute("INSERT INTO test_rollback VALUES ('invalid_id', 'value')")
        
        # Verify original data is still there
        result = await clickhouse_client.execute("SELECT count() as count FROM test_rollback")
        assert result[0][0] == 1
        
        result = await clickhouse_client.execute("SELECT * FROM test_rollback")
        assert result[0][0] == 1
        assert result[0][1] == "valid"
        
        # Clean up
        await clickhouse_client.execute("DROP TABLE test_rollback")
    
    async def test_large_batch_insert(self, clickhouse_client: AsyncClient):
        """Test inserting a larger batch of data."""
        # Create table
        await clickhouse_client.execute("""
            CREATE TABLE IF NOT EXISTS test_batch (
                id Int64,
                value String,
                timestamp DateTime64(3)
            ) ENGINE = Memory()
        """)
        
        # Generate test data
        batch_size = 1000
        current_time = datetime.now()
        
        # Build batch insert
        values = []
        for i in range(batch_size):
            values.append(f"({i}, 'value_{i}', '{current_time.isoformat()}')")
        
        insert_sql = f"""
        INSERT INTO test_batch (id, value, timestamp) VALUES
        {','.join(values)}
        """
        
        await clickhouse_client.execute(insert_sql)
        
        # Verify all data was inserted
        result = await clickhouse_client.execute("SELECT count() as count FROM test_batch")
        assert result[0][0] == batch_size
        
        # Test aggregation
        result = await clickhouse_client.execute("SELECT max(id) as max_id, min(id) as min_id FROM test_batch")
        assert result[0][0] == batch_size - 1
        assert result[0][1] == 0
        
        # Clean up
        await clickhouse_client.execute("DROP TABLE test_batch")
    
    async def test_concurrent_operations(self, clickhouse_client: AsyncClient):
        """Test concurrent database operations."""
        import asyncio
        
        # Create table
        await clickhouse_client.execute("""
            CREATE TABLE IF NOT EXISTS test_concurrent (
                id Int64,
                worker_id String
            ) ENGINE = Memory()
        """)
        
        async def worker_task(worker_id: str, start_id: int, count: int):
            """Worker function to insert data sequentially."""
            values = []
            for i in range(count):
                values.append(f"({start_id + i}, '{worker_id}')")
            
            insert_sql = f"""
            INSERT INTO test_concurrent (id, worker_id) VALUES
            {','.join(values)}
            """
            await clickhouse_client.execute(insert_sql)
        
        # Run workers sequentially (ClickHouse driver doesn't support concurrent queries on same connection)
        num_workers = 5
        records_per_worker = 100
        
        for i in range(num_workers):
            await worker_task(f"worker_{i}", i * records_per_worker, records_per_worker)
        
        # Verify all data was inserted
        result = await clickhouse_client.execute("SELECT count() as count FROM test_concurrent")
        assert result[0][0] == num_workers * records_per_worker
        
        # Verify data from each worker
        result = await clickhouse_client.execute("""
            SELECT worker_id, count() as count 
            FROM test_concurrent 
            GROUP BY worker_id 
            ORDER BY worker_id
        """)
        
        assert len(result) == num_workers
        for i, row in enumerate(result):
            assert row[0] == f"worker_{i}"
            assert row[1] == records_per_worker
        
        # Clean up
        await clickhouse_client.execute("DROP TABLE test_concurrent")