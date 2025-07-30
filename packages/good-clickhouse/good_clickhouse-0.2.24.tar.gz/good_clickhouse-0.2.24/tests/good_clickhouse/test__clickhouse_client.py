import os
import pytest
import unittest.mock
from unittest.mock import patch, MagicMock
from clickhouse_driver.dbapi.connection import Connection
from clickhouse_driver.dbapi.extras import NamedTupleCursor

from good_clickhouse import (
    Clickhouse,
    ClickhouseProvider,
    ClickhouseAsync,
    ConnectionProfile,
)


@pytest.fixture
def mock_connection():
    connection = MagicMock(spec=Connection)
    cursor = MagicMock(spec=NamedTupleCursor)
    connection.cursor.return_value = cursor
    return connection


@pytest.fixture
def mock_clickhouse_provider(mock_connection):
    with patch(
        "good_clickhouse.ClickhouseProvider.provide",
        return_value=Clickhouse(mock_connection),
    ):
        yield ClickhouseProvider()


@pytest.fixture
def mock_async_clickhouse_provider(mock_clickhouse_provider):
    with patch("good_clickhouse.ClickhouseAsync") as async_client_mock:
        async_client_mock.return_value = MagicMock()
        yield ClickhouseAsync(sync_client=mock_clickhouse_provider.get())


def test_connection_profile_load_by_prefix():
    config = {
        "CLICKHOUSE_HOST": "localhost",
        "CLICKHOUSE_PORT": "9000",
        "CLICKHOUSE_DATABASE": "test_db",
        "CLICKHOUSE_USER": "default",
        "CLICKHOUSE_PASSWORD": "secret",
        "CLICKHOUSE_SECURE": "False",
        "CLICKHOUSE_COMPRESSION": "False",
    }
    profile = ConnectionProfile.load_by_prefix("CLICKHOUSE", config)
    assert profile.host == "localhost"
    assert profile.port == 9000
    assert profile.database == "test_db"
    assert profile.user == "default"
    assert profile.password.get_secret_value() == "secret"
    assert profile.secure is False
    assert profile.compression is False
    assert profile.model_dump(mode="json") == {
        "host": "localhost",
        "port": 9000,
        "database": "test_db",
        "user": "default",
        "password": "secret",
        "secure": False,
        "compression": False,
    }


def test_clickhouse_provider_provide(mock_clickhouse_provider, mock_connection):
    clickhouse_instance = mock_clickhouse_provider.provide()
    assert isinstance(clickhouse_instance, Clickhouse)
    assert clickhouse_instance.connection == mock_connection


def test_clickhouse_enter_exit(mock_connection):
    clickhouse = Clickhouse(connection=mock_connection)
    with clickhouse as cursor:
        assert cursor == mock_connection.cursor.return_value
    mock_connection.cursor.return_value.close.assert_called_once()
    mock_connection.close.assert_called_once()


@pytest.mark.asyncio
async def test_clickhouse_async_provide(mock_async_clickhouse_provider):
    async with mock_async_clickhouse_provider as async_client:
        assert async_client == mock_async_clickhouse_provider.connection


@pytest.mark.asyncio
async def test_clickhouse_async_enter_exit(mock_async_clickhouse_provider):
    async with mock_async_clickhouse_provider as async_client:
        assert async_client is not None
    # You can add assertions here if needed for closing the async connection


def test_clickhouse_provider_with_profile():
    """Test that ClickhouseProvider correctly loads profile from environment variables."""
    # Set up environment variables for CLOUD profile
    test_env = {
        "CLICKHOUSE_CLOUD_HOST": "cloud.clickhouse.com",
        "CLICKHOUSE_CLOUD_PORT": "8443",
        "CLICKHOUSE_CLOUD_DATABASE": "cloud_db",
        "CLICKHOUSE_CLOUD_USER": "cloud_user",
        "CLICKHOUSE_CLOUD_PASSWORD": "cloud_pass",
        "CLICKHOUSE_CLOUD_SECURE": "true",
        "CLICKHOUSE_CLOUD_COMPRESSION": "true",
    }
    
    with patch.dict('os.environ', test_env):
        with patch('good_clickhouse._client.connect') as mock_connect:
            # Test profile loading with uppercase profile name
            provider = ClickhouseProvider(profile='CLOUD')
            provider.get()  # Use get() to trigger the actual provider logic
            
            # Verify connect was called with correct parameters from environment
            mock_connect.assert_called_once_with(
                host="cloud.clickhouse.com",
                port=8443,
                database="cloud_db", 
                user="cloud_user",
                password="cloud_pass",
                secure=True,
                compression=True
            )
            
            mock_connect.reset_mock()
            
            # Test profile loading with lowercase profile name (should add CLICKHOUSE_ prefix)
            provider = ClickhouseProvider(profile='cloud')
            provider.get()
            
            # Should produce same result
            mock_connect.assert_called_once_with(
                host="cloud.clickhouse.com",
                port=8443,
                database="cloud_db",
                user="cloud_user", 
                password="cloud_pass",
                secure=True,
                compression=True
            )


def test_clickhouse_provider_profile_with_overrides():
    """Test that direct parameters override profile settings.
    
    NOTE: Due to current implementation, only non-connection parameters 
    (secure, compression, database) can be overridden when using profiles.
    Connection parameters (host, port, user, password) cannot be overridden.
    """
    test_env = {
        "CLICKHOUSE_PROD_HOST": "prod.clickhouse.com",
        "CLICKHOUSE_PROD_PORT": "9000",
        "CLICKHOUSE_PROD_DATABASE": "prod_db",
        "CLICKHOUSE_PROD_USER": "prod_user",
        "CLICKHOUSE_PROD_PASSWORD": "prod_pass",
        "CLICKHOUSE_PROD_SECURE": "false",
        "CLICKHOUSE_PROD_COMPRESSION": "false",
    }
    
    with patch.dict('os.environ', test_env):
        with patch('good_clickhouse._client.connect') as mock_connect:
            # Test that direct parameters override profile settings
            # NOTE: port cannot be overridden due to current implementation
            provider = ClickhouseProvider(
                profile='PROD',
                database='override_db',
                secure=True,
                compression=True
            )
            provider.get()
            
            # Verify connect was called with overridden parameters
            mock_connect.assert_called_once_with(
                host="prod.clickhouse.com",  # from profile (cannot override)
                port=9000,  # from profile (cannot override)
                database="override_db",  # overridden
                user="prod_user",  # from profile (cannot override)
                password="prod_pass",  # from profile (cannot override)
                secure=True,  # overridden
                compression=True  # overridden
            )


def test_clickhouse_provider_profile_not_found():
    """Test behavior when profile environment variables don't exist."""
    # Clear any existing CLICKHOUSE env vars
    clean_env = {k: v for k, v in os.environ.items() if not k.startswith('CLICKHOUSE_')}
    
    with patch.dict('os.environ', clean_env, clear=True):
        with patch('good_clickhouse._client.connect') as mock_connect:
            # Should use defaults when profile env vars don't exist
            provider = ClickhouseProvider(profile='NONEXISTENT')
            provider.get()
            
            # Should use default values
            mock_connect.assert_called_once_with(
                host="localhost",
                port=9000,
                database="default",
                user="default",
                secure=False,
                compression=False
            )


def test_clickhouse_provider_profile_partial_config():
    """Test profile loading with only some environment variables set."""
    test_env = {
        "CLICKHOUSE_PARTIAL_HOST": "partial.clickhouse.com",
        "CLICKHOUSE_PARTIAL_USER": "partial_user",
        # Other vars not set - should use defaults
    }
    
    with patch.dict('os.environ', test_env):
        with patch('good_clickhouse._client.connect') as mock_connect:
            provider = ClickhouseProvider(profile='PARTIAL')
            provider.get()
            
            # Should use mix of profile values and defaults
            mock_connect.assert_called_once_with(
                host="partial.clickhouse.com",  # from profile
                port=9000,  # default
                database="default",  # default
                user="partial_user",  # from profile
                secure=False,  # default
                compression=False  # default
            )


def test_clickhouse_provider_profile_limitation():
    """Test demonstrates current limitation where connection params cannot be overridden."""
    test_env = {
        "CLICKHOUSE_TEST_HOST": "test.clickhouse.com",
        "CLICKHOUSE_TEST_PORT": "9000",
        "CLICKHOUSE_TEST_USER": "test_user",
        "CLICKHOUSE_TEST_PASSWORD": "test_pass",
    }
    
    with patch.dict('os.environ', test_env):
        with patch('good_clickhouse._client.connect') as mock_connect:
            # Attempt to override connection parameters - they will be ignored
            provider = ClickhouseProvider(
                profile='TEST',
                host='override.clickhouse.com',  # Will be ignored
                port=8443,  # Will be ignored 
                user='override_user',  # Will be ignored
                password='override_pass'  # Will be ignored
            )
            provider.get()
            
            # Connection params from profile are used, overrides are ignored
            mock_connect.assert_called_once_with(
                host="test.clickhouse.com",  # from profile, not override
                port=9000,  # from profile, not override
                database="default",
                user="test_user",  # from profile, not override
                password="test_pass",  # from profile, not override
                secure=False,
                compression=False
            )


@pytest.mark.asyncio
async def test_clickhouse_async_provider_with_profile():
    """Test that ClickhouseAsyncProvider correctly loads profile from environment variables."""
    test_env = {
        "CLICKHOUSE_CLOUD_HOST": "cloud.clickhouse.com",
        "CLICKHOUSE_CLOUD_PORT": "8443",
        "CLICKHOUSE_CLOUD_DATABASE": "cloud_db",
        "CLICKHOUSE_CLOUD_USER": "cloud_user",
        "CLICKHOUSE_CLOUD_PASSWORD": "cloud_pass",
        "CLICKHOUSE_CLOUD_SECURE": "true",
        "CLICKHOUSE_CLOUD_COMPRESSION": "true",
    }
    
    with patch.dict('os.environ', test_env):
        with patch('good_clickhouse._client.connect') as mock_connect:
            # Create a mock connection that the sync client would use
            mock_connection = MagicMock()
            mock_connect.return_value = mock_connection
            
            # This should work but currently fails with "host or dsn is required"
            from good_clickhouse import ClickhouseAsyncProvider
            provider = ClickhouseAsyncProvider(profile='CLOUD')
            
            # Try to get the async client
            client = await provider.get()
            
            # The fix should have created the sync client with profile params
            # Check that connect was called with the profile parameters
            assert mock_connect.call_count >= 1
            
            # Find the call with profile parameters
            profile_call_found = False
            for call in mock_connect.call_args_list:
                if call == unittest.mock.call(
                    host="cloud.clickhouse.com",
                    port=8443,
                    database="cloud_db",
                    user="cloud_user",
                    password="cloud_pass",
                    secure=True,
                    compression=True
                ):
                    profile_call_found = True
                    break
            
            assert profile_call_found, f"Profile parameters not passed to connect. Calls: {mock_connect.call_args_list}"


@pytest.mark.asyncio 
async def test_clickhouse_async_provider_without_profile():
    """Test that ClickhouseAsyncProvider works with direct parameters."""
    with patch('good_clickhouse._client.connect') as mock_connect:
        # Create a mock connection
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        
        from good_clickhouse import ClickhouseAsyncProvider
        provider = ClickhouseAsyncProvider(
            host="test.clickhouse.com",
            port=9000,
            database="test_db",
            user="test_user"
        )
        
        # This should work
        client = await provider.get()
        
        # Similar to the profile test, check that the parameters were passed
        assert mock_connect.call_count >= 1
        
        # Find the call with our parameters
        params_call_found = False
        for call in mock_connect.call_args_list:
            args, kwargs = call
            if (kwargs.get('host') == "test.clickhouse.com" and
                kwargs.get('port') == 9000 and
                kwargs.get('database') == "test_db" and
                kwargs.get('user') == "test_user"):
                params_call_found = True
                break
        
        assert params_call_found, f"Direct parameters not passed to connect. Calls: {mock_connect.call_args_list}"
