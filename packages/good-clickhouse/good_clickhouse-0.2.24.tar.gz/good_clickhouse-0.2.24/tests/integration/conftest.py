import asyncio
import subprocess
import time
import pytest
from good_clickhouse import ConnectionProfile


CLICKHOUSE_TEST_PORT = 19000
CLICKHOUSE_HTTP_PORT = 18123
CLICKHOUSE_CONTAINER_NAME = "clickhouse-integration-test"


def is_clickhouse_ready() -> bool:
    """Check if ClickHouse is ready to accept connections."""
    try:
        result = subprocess.run([
            "docker", "exec", CLICKHOUSE_CONTAINER_NAME,
            "clickhouse-client", "--host=localhost", f"--port={9000}",
            "--user=default", "--query=SELECT 1"
        ], capture_output=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        return False


def start_clickhouse_container():
    """Start an ephemeral ClickHouse container for testing."""
    # Stop and remove any existing container
    subprocess.run([
        "docker", "stop", CLICKHOUSE_CONTAINER_NAME
    ], capture_output=True)
    subprocess.run([
        "docker", "rm", CLICKHOUSE_CONTAINER_NAME
    ], capture_output=True)
    
    # Start new container
    cmd = [
        "docker", "run", "-d",
        "--name", CLICKHOUSE_CONTAINER_NAME,
        "-p", f"{CLICKHOUSE_TEST_PORT}:9000",
        "-p", f"{CLICKHOUSE_HTTP_PORT}:8123",
        "--tmpfs", "/var/lib/clickhouse:noexec,nosuid,size=1g",
        "-e", "CLICKHOUSE_DB=test_db",
        "-e", "CLICKHOUSE_USER=default",
        "-e", "CLICKHOUSE_PASSWORD=testpass",
        "clickhouse/clickhouse-server:24.11-alpine"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to start ClickHouse container: {result.stderr}")
    
    # Wait for ClickHouse to be ready
    max_attempts = 30
    for attempt in range(max_attempts):
        if is_clickhouse_ready():
            print(f"ClickHouse ready after {attempt + 1} attempts")
            return
        time.sleep(1)
    
    # Get container logs for debugging
    logs_result = subprocess.run([
        "docker", "logs", CLICKHOUSE_CONTAINER_NAME
    ], capture_output=True, text=True)
    
    raise RuntimeError(f"ClickHouse not ready after {max_attempts} seconds. Logs: {logs_result.stdout}")


def stop_clickhouse_container():
    """Stop and remove the ClickHouse container."""
    subprocess.run([
        "docker", "stop", CLICKHOUSE_CONTAINER_NAME
    ], capture_output=True)
    subprocess.run([
        "docker", "rm", CLICKHOUSE_CONTAINER_NAME
    ], capture_output=True)


@pytest.fixture(scope="module", autouse=True)
def clickhouse_container():
    """Module-scoped fixture to manage ClickHouse container lifecycle."""
    start_clickhouse_container()
    import time
    time.sleep(2)  # Extra time for stability
    yield
    stop_clickhouse_container()


@pytest.fixture
def clickhouse_profile():
    """Connection profile for test ClickHouse instance."""
    from pydantic import SecretStr
    return ConnectionProfile(
        host="localhost",
        port=CLICKHOUSE_TEST_PORT,
        database="test_db",
        user="default",
        password=SecretStr("testpass"),
        secure=False,
        compression=False
    )


@pytest.fixture
async def clickhouse_client(clickhouse_profile):
    """Async ClickHouse client for integration tests."""
    from good_clickhouse._client import ClickhouseAsync, Clickhouse
    from clickhouse_driver import connect
    from aioch import Client as AsyncClient
    import time
    
    # Ensure container is ready
    time.sleep(1)
    
    # Create fresh connection for each test
    connection_params = {
        "host": clickhouse_profile.host,
        "port": clickhouse_profile.port,
        "database": clickhouse_profile.database,
        "user": clickhouse_profile.user,
        "secure": clickhouse_profile.secure,
        "compression": clickhouse_profile.compression
    }
    
    if clickhouse_profile.password:
        connection_params["password"] = clickhouse_profile.password.get_secret_value()
    
    connection = connect(**connection_params)
    sync_client = Clickhouse(connection=connection)
    async_client = object.__new__(ClickhouseAsync)
    async_client.connection = AsyncClient(_client=sync_client.connection._make_client())
    
    async with async_client as client:
        yield client


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()