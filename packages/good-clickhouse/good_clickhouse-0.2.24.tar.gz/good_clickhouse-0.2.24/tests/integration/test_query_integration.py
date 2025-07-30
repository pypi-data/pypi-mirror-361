import pytest
from datetime import datetime
from good_clickhouse.query import sql
from aioch import Client as AsyncClient


@pytest.mark.asyncio
class TestQueryIntegration:
    
    async def test_basic_query_decorator(self, clickhouse_client: AsyncClient):
        """Test basic @query decorator functionality with real ClickHouse."""
        
        @sql
        def get_test_value():
            '''SELECT 1 as test_value'''
        
        # Execute the query
        result = await clickhouse_client.execute(get_test_value())
        assert result == [{"test_value": 1}]
    
    async def test_parameterized_query(self, clickhouse_client: AsyncClient):
        """Test query with parameters."""
        
        # Setup test table
        await clickhouse_client.execute("""
        CREATE TABLE IF NOT EXISTS query_test_users (
            id Int64,
            name String,
            age Int32,
            active Bool
        ) ENGINE = Memory()
        """)
        
        # Insert test data
        await clickhouse_client.execute("""
        INSERT INTO query_test_users VALUES 
        (1, 'Alice', 25, true),
        (2, 'Bob', 30, false),
        (3, 'Charlie', 35, true),
        (4, 'Diana', 28, true)
        """)
        
        @sql
        def get_users_by_age(min_age: int, active_only: bool = False):
            '''
            SELECT name, age 
            FROM query_test_users 
            WHERE age >= {{ min_age }}
            {% if active_only %}
            AND active = true
            {% endif %}
            ORDER BY age
            '''
        
        # Test with just min_age
        result = await clickhouse_client.execute(get_users_by_age(30))
        assert len(result) == 2
        assert result[0]["name"] == "Bob"
        assert result[1]["name"] == "Charlie"
        
        # Test with min_age and active_only
        result = await clickhouse_client.execute(get_users_by_age(25, True))
        assert len(result) == 2
        assert result[0]["name"] == "Alice"
        assert result[1]["name"] == "Charlie"
        
        # Clean up
        await clickhouse_client.execute("DROP TABLE query_test_users")
    
    async def test_composable_queries(self, clickhouse_client: AsyncClient):
        """Test queries that compose other queries."""
        
        # Setup test table
        await clickhouse_client.execute("""
        CREATE TABLE IF NOT EXISTS composable_test (
            id Int64,
            name String,
            status String,
            created_at DateTime64(3),
            deleted_at Nullable(DateTime64(3))
        ) ENGINE = Memory()
        """)
        
        # Insert test data
        await clickhouse_client.execute(f"""
        INSERT INTO composable_test VALUES 
        (1, 'Active User', 'active', '{datetime.now().isoformat()}', NULL),
        (2, 'Inactive User', 'inactive', '{datetime.now().isoformat()}', NULL),
        (3, 'Deleted User', 'active', '{datetime.now().isoformat()}', '{datetime.now().isoformat()}')
        """)
        
        @sql
        def base_filter():
            '''WHERE deleted_at IS NULL'''
        
        @sql
        def active_filter():
            '''AND status = 'active' '''
        
        @sql
        def get_active_users():
            '''
            SELECT id, name, status
            FROM composable_test
            {{ base_filter() }}
            {{ active_filter() }}
            ORDER BY id
            '''
        
        @sql
        def get_all_non_deleted():
            '''
            SELECT id, name, status
            FROM composable_test
            {{ base_filter() }}
            ORDER BY id
            '''
        
        # Test composed query for active users
        result = await clickhouse_client.execute(get_active_users())
        assert len(result) == 1
        assert result[0]["name"] == "Active User"
        
        # Test composed query for all non-deleted
        result = await clickhouse_client.execute(get_all_non_deleted())
        assert len(result) == 2
        assert result[0]["name"] == "Active User"
        assert result[1]["name"] == "Inactive User"
        
        # Clean up
        await clickhouse_client.execute("DROP TABLE composable_test")
    
    async def test_query_with_environment_variables(self, clickhouse_client: AsyncClient):
        """Test query with environment variables."""
        import os
        
        # Set test environment variable
        test_table_name = "env_test_table"
        os.environ["TEST_TABLE_NAME"] = test_table_name
        
        # Setup test table
        await clickhouse_client.execute(f"""
        CREATE TABLE IF NOT EXISTS {test_table_name} (
            id Int64,
            value String
        ) ENGINE = Memory()
        """)
        
        await clickhouse_client.execute(f"""
        INSERT INTO {test_table_name} VALUES (1, 'test_value')
        """)
        
        @sql
        def get_from_env_table():
            '''
            SELECT * FROM {{ env("TEST_TABLE_NAME") }}
            ORDER BY id
            '''
        
        # Test query using environment variable
        result = await clickhouse_client.execute(get_from_env_table())
        assert len(result) == 1
        assert result[0]["id"] == 1
        assert result[0]["value"] == "test_value"
        
        # Clean up
        await clickhouse_client.execute(f"DROP TABLE {test_table_name}")
        del os.environ["TEST_TABLE_NAME"]
    
    async def test_query_with_complex_template(self, clickhouse_client: AsyncClient):
        """Test query with complex Jinja2 templating."""
        
        # Setup test table
        await clickhouse_client.execute("""
        CREATE TABLE IF NOT EXISTS complex_query_test (
            id Int64,
            category String,
            value Float64,
            created_date Date,
            tags Array(String)
        ) ENGINE = Memory()
        """)
        
        # Insert test data
        await clickhouse_client.execute("""
        INSERT INTO complex_query_test VALUES 
        (1, 'A', 10.5, '2024-01-01', ['tag1', 'tag2']),
        (2, 'B', 20.3, '2024-01-02', ['tag2', 'tag3']),
        (3, 'A', 15.7, '2024-01-03', ['tag1']),
        (4, 'C', 5.2, '2024-01-04', ['tag3', 'tag4']),
        (5, 'B', 25.1, '2024-01-05', ['tag2'])
        """)
        
        @sql
        def complex_filtered_query(categories=None, min_value=None, has_tag=None, include_stats=False, include_tags=False):
            '''
            SELECT 
                category,
                {% if include_stats %}
                count() as count,
                avg(value) as avg_value,
                max(value) as max_value,
                {% endif %}
                {% if include_tags %}
                groupArray(tags) as all_tags
                {% endif %}
                id, value
            FROM complex_query_test
            WHERE 1=1
            {% if categories %}
            AND category IN ({{ categories | map('quote') | join(', ') }})
            {% endif %}
            {% if min_value %}
            AND value >= {{ min_value }}
            {% endif %}
            {% if has_tag %}
            AND has(tags, {{ has_tag | quote }})
            {% endif %}
            {% if include_stats %}
            GROUP BY category
            {% endif %}
            ORDER BY 
            {% if include_stats %}
            category
            {% else %}
            id
            {% endif %}
            '''
        
        # Test with categories filter
        result = await clickhouse_client.execute(
            complex_filtered_query(categories=['A', 'B'])
        )
        assert len(result) == 4  # 2 A's + 2 B's
        
        # Test with stats aggregation
        result = await clickhouse_client.execute(
            complex_filtered_query(
                categories=['A', 'B'], 
                include_stats=True
            )
        )
        assert len(result) == 2  # Grouped by category
        assert result[0]["category"] == "A"
        assert result[0]["count"] == 2
        assert result[1]["category"] == "B"
        assert result[1]["count"] == 2
        
        # Test with tag filter
        result = await clickhouse_client.execute(
            complex_filtered_query(has_tag='tag1')
        )
        assert len(result) == 2  # Records with tag1
        
        # Test with value filter
        result = await clickhouse_client.execute(
            complex_filtered_query(min_value=20.0)
        )
        assert len(result) == 2  # Records with value >= 20
        
        # Clean up
        await clickhouse_client.execute("DROP TABLE complex_query_test")
    
    async def test_query_error_handling(self, clickhouse_client: AsyncClient):
        """Test query error handling with real ClickHouse."""
        
        @sql
        def invalid_query():
            '''SELECT FROM invalid_table_that_does_not_exist'''
        
        @sql
        def syntax_error_query():
            '''SELECT * FORM non_existent_table'''  # Intentional typo
        
        # Test table not found error
        with pytest.raises(Exception):
            await clickhouse_client.execute(invalid_query())
        
        # Test syntax error
        with pytest.raises(Exception):
            await clickhouse_client.execute(syntax_error_query())
    
    async def test_query_with_large_result_set(self, clickhouse_client: AsyncClient):
        """Test query that returns a large result set."""
        
        # Setup test table with many rows
        await clickhouse_client.execute("""
        CREATE TABLE IF NOT EXISTS large_result_test (
            id Int64,
            value String,
            number Float64
        ) ENGINE = Memory()
        """)
        
        # Insert large dataset using a single query
        batch_size = 10000
        values = []
        for i in range(batch_size):
            values.append(f"({i}, 'value_{i}', {i * 1.5})")
        
        # Insert in chunks to avoid too large queries
        chunk_size = 1000
        for i in range(0, len(values), chunk_size):
            chunk = values[i:i + chunk_size]
            insert_sql = f"""
            INSERT INTO large_result_test (id, value, number) VALUES
            {','.join(chunk)}
            """
            await clickhouse_client.execute(insert_sql)
        
        @sql
        def get_large_dataset(limit_rows=None):
            '''
            SELECT id, value, number
            FROM large_result_test
            {% if limit_rows %}
            LIMIT {{ limit_rows }}
            {% endif %}
            ORDER BY id
            '''
        
        # Test getting all rows
        result = await clickhouse_client.execute(get_large_dataset())
        assert len(result) == batch_size
        
        # Test with limit
        result = await clickhouse_client.execute(get_large_dataset(100))
        assert len(result) == 100
        assert result[0]["id"] == 0
        assert result[99]["id"] == 99
        
        # Test aggregation on large dataset
        @sql
        def aggregate_large_dataset():
            '''
            SELECT 
                count() as total_count,
                avg(number) as avg_number,
                max(number) as max_number,
                min(number) as min_number
            FROM large_result_test
            '''
        
        result = await clickhouse_client.execute(aggregate_large_dataset())
        row = result[0]
        assert row["total_count"] == batch_size
        assert abs(row["avg_number"] - ((batch_size - 1) * 1.5 / 2)) < 1.0  # Approximate average
        assert row["max_number"] == (batch_size - 1) * 1.5
        assert row["min_number"] == 0.0
        
        # Clean up
        await clickhouse_client.execute("DROP TABLE large_result_test")