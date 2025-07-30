.PHONY: test test-unit test-integration test-all clean setup

# Run unit tests (mocked, no Docker required)
test-unit:
	uv run pytest tests/good_clickhouse/ -v

# Run integration tests (requires Docker)
test-integration:
	uv run pytest tests/integration/ -v

# Run all tests
test-all: test-unit test-integration

# Default test command (unit tests only)
test: test-unit

# Setup development environment
setup:
	uv sync --group dev --group integration

# Clean up any running test containers
clean:
	-docker stop clickhouse-integration-test 2>/dev/null
	-docker rm clickhouse-integration-test 2>/dev/null

# Check if Docker is available for integration tests
check-docker:
	@docker info >/dev/null 2>&1 || (echo "Docker is not running. Integration tests require Docker." && exit 1)
	@echo "Docker is available for integration tests"

# Run integration tests with Docker check
test-integration-safe: check-docker test-integration