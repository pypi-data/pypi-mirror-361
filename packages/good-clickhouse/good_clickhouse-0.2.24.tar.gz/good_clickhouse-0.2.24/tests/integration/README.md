# Integration Tests

These integration tests run against a real ClickHouse instance using Docker. They verify that the good-clickhouse library works correctly with actual ClickHouse database operations.

## Prerequisites

- Docker must be installed and running
- Port 19000 (ClickHouse native) and 18123 (HTTP) must be available

## Running Integration Tests

From the good-clickhouse directory:

```bash
# Run all integration tests
uv run pytest tests/integration/ -v

# Run specific integration test file
uv run pytest tests/integration/test_client_integration.py -v

# Run with additional output
uv run pytest tests/integration/ -v -s
```

## Test Structure

### `conftest.py`
- Manages Docker container lifecycle
- Provides ClickHouse connection fixtures
- Uses non-standard ports (19000, 18123) to avoid conflicts

### `test_client_integration.py`
- Tests basic client connectivity and operations
- Verifies data type handling and round-trip conversion
- Tests transaction behavior and error handling
- Includes concurrent operation testing

### `test_collection_integration.py`
- Tests PydanticCollection with real ClickHouse insertion
- Verifies field exclusions and column ordering
- Tests large batch operations
- Validates computed fields and serialization

### `test_query_integration.py`
- Tests @sql decorator with actual database
- Verifies parameterized and composable queries
- Tests environment variable substitution
- Includes complex Jinja2 templating scenarios

## Container Management

The tests automatically:
1. Start a ClickHouse container before tests begin
2. Wait for ClickHouse to be ready (up to 30 seconds)
3. Clean up the container after tests complete

The container uses:
- Image: `clickhouse/clickhouse-server:24.11-alpine`
- Ports: 19000 (native), 18123 (HTTP)
- Database: `test_db`
- User: `default` (no password)
- Storage: tmpfs (in-memory, ephemeral)

## Debugging

If tests fail due to container issues:

```bash
# Check if container is running
docker ps | grep clickhouse-integration-test

# View container logs
docker logs clickhouse-integration-test

# Manually connect to test database
docker exec -it clickhouse-integration-test clickhouse-client --database=test_db

# Clean up manually if needed
docker stop clickhouse-integration-test
docker rm clickhouse-integration-test
```

## Performance Notes

- Tests use in-memory storage (tmpfs) for speed
- Large batch tests insert up to 10,000 records
- Concurrent tests run 5 workers simultaneously
- All test tables are automatically cleaned up

These integration tests complement the unit tests by verifying real-world database interactions and ensuring the library works correctly with actual ClickHouse instances.