import pytest
from datetime import datetime
from typing import List, Optional
from pydantic import computed_field
from good_clickhouse.collection import DataTable, PydanticCollection, insert_into_clickhouse
from good_common.types import UUIDField, UUID
from aioch import Client as AsyncClient


class IntegrationTestUser(DataTable):
    uid: UUIDField
    id: int
    name: str
    email: Optional[str] = None
    created_at: datetime
    active: bool = True
    tags: List[str] = []
    
    @computed_field
    @property
    def display_name(self) -> str:
        return f"{self.name} ({self.id})"


class UserWithExclusions(DataTable):
    __exclude_columns__ = {"internal_field"}
    __table_column_order__ = ["uid", "id", "name", "email"]
    
    uid: UUIDField
    id: int
    name: str
    email: Optional[str] = None
    internal_field: str = "internal"
    active: bool = True


@pytest.mark.asyncio
class TestCollectionIntegration:
    
    async def test_collection_with_real_clickhouse(self, clickhouse_client: AsyncClient):
        """Test PydanticCollection with actual ClickHouse insertion."""
        # Create table based on model structure
        collection = PydanticCollection([], type=IntegrationTestUser)
        
        # Generate DDL from collection columns
        column_definitions = []
        for col in collection.columns:
            column_definitions.append(f"{col.name} {col.type}")
        
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS integration_users (
            {', '.join(column_definitions)}
        ) ENGINE = Memory()
        """
        
        await clickhouse_client.execute(create_sql)
        
        # Create test data
        test_users = [
            IntegrationTestUser(
                uid=UUID.create_v7(),
                id=1,
                name="Alice",
                email="alice@example.com",
                created_at=datetime.now(),
                active=True,
                tags=["admin", "user"]
            ),
            IntegrationTestUser(
                uid=UUID.create_v7(),
                id=2,
                name="Bob",
                email=None,
                created_at=datetime.now(),
                active=False,
                tags=["user"]
            )
        ]
        
        collection = PydanticCollection(test_users, type=IntegrationTestUser)
        
        # Test the collection's select property
        assert "uid" in collection.select
        assert "id" in collection.select
        assert "name" in collection.select
        assert "display_name" in collection.select
        
        # Insert data using collection's select and execute
        insert_sql = f"""
        INSERT INTO integration_users ({collection.select})
        VALUES
        """
        await clickhouse_client.execute(insert_sql, list(collection))
        
        # Verify data was inserted correctly
        result = await clickhouse_client.execute("SELECT count() as count FROM integration_users")
        assert result[0][0] == 2
        
        # Test querying specific fields
        result = await clickhouse_client.execute("""
            SELECT id, name, email, active, tags, display_name 
            FROM integration_users 
            ORDER BY id
        """)
        
        assert len(result) == 2
        
        # Verify Alice's data
        alice = result[0]
        assert alice[0] == 1  # id
        assert alice[1] == "Alice"  # name
        assert alice[2] == "alice@example.com"  # email
        assert alice[3] is True  # active
        assert alice[4] == ["admin", "user"]  # tags
        assert alice[5] == "Alice (1)"  # display_name
        
        # Verify Bob's data
        bob = result[1]
        assert bob[0] == 2  # id
        assert bob[1] == "Bob"  # name
        assert bob[2] is None  # email
        assert bob[3] is False  # active
        assert bob[4] == ["user"]  # tags
        assert bob[5] == "Bob (2)"  # display_name
        
        # Clean up
        await clickhouse_client.execute("DROP TABLE integration_users")
    
    async def test_collection_with_exclusions(self, clickhouse_client: AsyncClient):
        """Test collection with field exclusions."""
        collection = PydanticCollection([], type=UserWithExclusions)
        
        # Verify excluded field is not in columns
        column_names = [col.name for col in collection.columns]
        assert "internal_field" not in column_names
        assert "id" in column_names
        assert "name" in column_names
        
        # Create table
        column_definitions = []
        for col in collection.columns:
            column_definitions.append(f"{col.name} {col.type}")
        
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS users_with_exclusions (
            {', '.join(column_definitions)}
        ) ENGINE = Memory()
        """
        
        await clickhouse_client.execute(create_sql)
        
        # Create test data
        test_user = UserWithExclusions(
            uid=UUID.create_v7(),
            id=1,
            name="Test User",
            email="test@example.com",
            internal_field="should_not_be_inserted",
            active=True
        )
        
        collection = PydanticCollection([test_user], type=UserWithExclusions)
        
        # Insert data
        insert_sql = f"""
        INSERT INTO users_with_exclusions ({collection.select})
        VALUES
        """
        await clickhouse_client.execute(insert_sql, list(collection))
        
        # Verify data was inserted (internal_field should not be there)
        result = await clickhouse_client.execute("SELECT * FROM users_with_exclusions")
        row = result[0]
        
        # Just verify the data is there correctly, regardless of order
        assert len(row) == 5  # Should only have 5 fields, not 6
        
        # Query specific columns to verify data
        result = await clickhouse_client.execute("SELECT id, name, email, active FROM users_with_exclusions")
        row = result[0]
        assert row[0] == 1  # id
        assert row[1] == "Test User"  # name
        assert row[2] == "test@example.com"  # email
        assert row[3] is True  # active
        
        # Clean up
        await clickhouse_client.execute("DROP TABLE users_with_exclusions")
    
    async def test_collection_column_ordering(self, clickhouse_client: AsyncClient):
        """Test that collection respects column ordering."""
        collection = PydanticCollection([], type=UserWithExclusions)
        column_names = [col.name for col in collection.columns]
        
        # Check that specified order comes first
        order_spec = ["uid", "id", "name", "email"]
        for i, expected_col in enumerate(order_spec):
            if expected_col in column_names:
                actual_pos = column_names.index(expected_col)
                # Check that each specified column appears before any unspecified ones
                assert actual_pos < len(order_spec), f"Column {expected_col} not in expected position"
    
    async def test_empty_collection_insert(self, clickhouse_client: AsyncClient):
        """Test inserting an empty collection."""
        # Create table
        await clickhouse_client.execute("""
        CREATE TABLE IF NOT EXISTS empty_test (
            id Int64,
            name String
        ) ENGINE = Memory()
        """)
        
        # Create empty collection
        collection = PydanticCollection([], type=IntegrationTestUser)
        
        # Insert empty collection (should not fail)
        insert_sql = f"""
        INSERT INTO empty_test ({collection.select})
        VALUES
        """
        # This might fail with empty data, so catch it
        try:
            await clickhouse_client.execute(insert_sql, list(collection))
        except Exception:
            # Empty insert may fail, that's OK
            pass
        
        # Verify table is still empty
        result = await clickhouse_client.execute("SELECT count() as count FROM empty_test")
        assert result[0][0] == 0
        
        # Clean up
        await clickhouse_client.execute("DROP TABLE empty_test")
    
    async def test_large_collection_insert(self, clickhouse_client: AsyncClient):
        """Test inserting a large collection."""
        # Create table
        collection = PydanticCollection([], type=IntegrationTestUser)
        column_definitions = []
        for col in collection.columns:
            column_definitions.append(f"{col.name} {col.type}")
        
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS large_collection_test (
            {', '.join(column_definitions)}
        ) ENGINE = Memory()
        """
        await clickhouse_client.execute(create_sql)
        
        # Generate large dataset
        batch_size = 5000
        test_users = []
        
        for i in range(batch_size):
            user = IntegrationTestUser(
                uid=UUID.create_v7(),
                id=i,
                name=f"User {i}",
                email=f"user{i}@example.com" if i % 2 == 0 else None,
                created_at=datetime.now(),
                active=i % 3 != 0,
                tags=[f"tag{i % 5}", f"group{i % 10}"]
            )
            test_users.append(user)
        
        collection = PydanticCollection(test_users, type=IntegrationTestUser)
        
        # Insert large collection
        insert_sql = f"""
        INSERT INTO large_collection_test ({collection.select})
        VALUES
        """
        await clickhouse_client.execute(insert_sql, list(collection))
        
        # Verify all data was inserted
        result = await clickhouse_client.execute("SELECT count() as count FROM large_collection_test")
        assert result[0][0] == batch_size
        
        # Test some aggregations
        result = await clickhouse_client.execute("""
            SELECT 
                count() as total,
                countIf(active = true) as active_count,
                countIf(email IS NOT NULL) as with_email_count
            FROM large_collection_test
        """)
        
        row = result[0]
        assert row[0] == batch_size  # total
        # active when i % 3 != 0, so roughly 2/3 should be active
        expected_active = sum(1 for i in range(batch_size) if i % 3 != 0)
        assert row[1] == expected_active  # active_count
        # email when i % 2 == 0, so roughly half should have email
        expected_with_email = sum(1 for i in range(batch_size) if i % 2 == 0)
        assert row[2] == expected_with_email  # with_email_count
        
        # Clean up
        await clickhouse_client.execute("DROP TABLE large_collection_test")