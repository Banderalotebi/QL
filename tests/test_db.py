"""
Unit tests for Database Module
"""
import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from src.data.db import (
    DatabaseConnectionPool,
    get_pool,
    get_db_connection,
    with_retry
)


# Test the retry decorator
def test_with_retry_success():
    """Test retry decorator with successful function."""
    call_count = 0
    
    @with_retry
    def successful_func():
        nonlocal call_count
        call_count += 1
        return "success"
    
    result = successful_func()
    assert result == "success"
    assert call_count == 1


def test_with_retry_failure_then_success():
    """Test retry decorator recovers after failure."""
    call_count = 0
    
    @with_retry
    def flaky_func():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise Exception("Temporary failure")
        return "success"
    
    result = flaky_func()
    assert result == "success"
    assert call_count == 3


def test_with_retry_all_fail():
    """Test retry decorator gives up after max retries."""
    call_count = 0
    
    @with_retry
    def failing_func():
        nonlocal call_count
        call_count += 1
        raise Exception("Permanent failure")
    
    with pytest.raises(Exception):
        failing_func()
    
    # Should retry MAX_RETRIES times (default 3)
    assert call_count == 3


class TestDatabaseConnectionPool:
    """Tests for DatabaseConnectionPool class."""
    
    @patch('src.data.db.USE_SQLITE', True)
    def test_sqlite_connection(self):
        """Test getting SQLite connection."""
        pool = DatabaseConnectionPool()
        conn = pool.get_connection()
        
        assert conn is not None
        conn.close()
    
    def test_singleton_pattern(self):
        """Test that DatabaseConnectionPool is a singleton."""
        pool1 = get_pool()
        pool2 = get_pool()
        
        assert pool1 is pool2


class TestGetDbConnection:
    """Tests for get_db_connection context manager."""
    
    @patch('src.data.db.get_pool')
    def test_context_manager(self, mock_get_pool):
        """Test context manager acquires and releases connection."""
        mock_conn = MagicMock()
        mock_pool_instance = MagicMock()
        mock_pool_instance.get_connection.return_value = mock_conn
        mock_get_pool.return_value = mock_pool_instance
        
        with get_db_connection() as conn:
            assert conn == mock_conn
        
        mock_pool_instance.return_connection.assert_called_once_with(mock_conn)

