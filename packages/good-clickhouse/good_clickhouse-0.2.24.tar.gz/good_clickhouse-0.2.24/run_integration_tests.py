#!/usr/bin/env python3
"""
Simple integration test runner that bypasses pytest fixture complexity.
Run with: uv run python run_integration_tests.py
"""

import asyncio
import subprocess
import time
import sys
from pathlib import Path

# Add tests to path
sys.path.append(str(Path(__file__).parent / "tests" / "integration"))

from conftest import (
    start_clickhouse_container,
    stop_clickhouse_container,
    CLICKHOUSE_TEST_PORT
)

async def test_basic_integration():
    """Basic integration test without pytest complexity."""
    print("🚀 Starting ClickHouse integration test...")
    
    try:
        # Start container
        print("📦 Starting ClickHouse container...")
        start_clickhouse_container()
        
        # Give it extra time to be fully ready
        print("⏳ Waiting for ClickHouse to be fully ready...")
        time.sleep(3)
        
        # Test connection
        print("🔌 Testing connection...")
        from clickhouse_driver import connect
        from good_clickhouse._client import ClickhouseAsync, Clickhouse
        from aioch import Client as AsyncClient
        
        connection = connect(
            host="localhost",
            port=CLICKHOUSE_TEST_PORT,
            database="test_db",
            user="default",
            password="testpass"
        )
        
        sync_client = Clickhouse(connection=connection)
        async_client = object.__new__(ClickhouseAsync)
        async_client.connection = AsyncClient(_client=sync_client.connection._make_client())
        
        # Test basic query
        print("📊 Testing basic query...")
        async with async_client as client:
            result = await client.execute("SELECT 1 as test_value")
            print(f"✅ Basic query successful: {result}")
            
            # Test table creation
            print("🏗️  Testing table creation...")
            await client.execute("""
                CREATE TABLE IF NOT EXISTS test_integration (
                    id Int64,
                    name String
                ) ENGINE = Memory()
            """)
            print("✅ Table creation successful")
            
            # Test insertion
            print("📝 Testing data insertion...")
            await client.execute("INSERT INTO test_integration VALUES (1, 'test')")
            result = await client.execute("SELECT * FROM test_integration")
            print(f"✅ Data insertion and query successful: {result}")
            
            # Test SQL decorator
            print("🎯 Testing SQL decorator...")
            from good_clickhouse.query import sql
            
            @sql
            def get_test_data(table_name: str):
                '''SELECT * FROM {{ table_name }}'''
            
            result = await client.execute(get_test_data("test_integration"))
            print(f"✅ SQL decorator successful: {result}")
            
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        print("🧹 Cleaning up container...")
        stop_clickhouse_container()
        print("✅ Cleanup complete")

if __name__ == "__main__":
    success = asyncio.run(test_basic_integration())
    sys.exit(0 if success else 1)