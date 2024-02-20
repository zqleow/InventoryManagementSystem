import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from database_operations.crud import insert_item, get_items_within_date_range
from database_operations.models import DateRangeInput

@pytest.mark.asyncio
async def test_insert_new_item():
    # Mock the database pool
    db_pool_mock = MagicMock()

    # Mock the acquire and release methods of db_pool
    async def mock_acquire():
        return AsyncMock()

    async def mock_release(conn):
        pass

    db_pool_mock.acquire = AsyncMock(side_effect=mock_acquire)
    db_pool_mock.release = AsyncMock(side_effect=mock_release)

    # Define test item data
    test_item = {
        "name": "Test Item",
        "category": "Test Category",
        "price": "10.00"
    }

    # Mock the cursor and execute method
    mock_cursor = AsyncMock()
    mock_cursor.fetchone.return_value = None
    mock_cursor.lastrowid = 1

    # Mock the execute method of cursor
    async def mock_execute(query, values):
        pass

    mock_cursor.execute = AsyncMock(side_effect=mock_execute)

    # Mock the cursor return value
    async def mock_conn_cursor():
        return mock_cursor

    # Mock the execute method of connection
    async def mock_conn_execute(query, values):
        pass

    mock_conn = AsyncMock()
    mock_conn.execute = AsyncMock(side_effect=mock_conn_execute)

    # Patch the connection and cursor methods
    with patch("database_operations.crud.aiomysql.Pool.acquire", return_value=mock_conn), \
         patch("database_operations.crud.aiomysql.Connection.cursor", return_value=mock_conn_cursor):
        
        # Call insert_item function
        result = await insert_item(test_item, db_pool_mock)

        # Check if the result contains the expected item ID
        assert "id" in result


@pytest.mark.asyncio
async def test_update_existing_item():
    # Define the input item
    item = {
        "name": "Existing Item",
        "category": "Updated Category",
        "price": "30.00"
    }
    
    # Mock the aiomysql.Pool
    db_pool_mock = MagicMock()

    async def acquire_coro():
        # Create a MagicMock for the connection
        conn_mock = AsyncMock()

        # Define a cursor coroutine function
        async def cursor_coro():
            # Create a MagicMock for the cursor
            cursor_mock = AsyncMock()

            # Define the fetchone coroutine function
            async def fetchone_coro():
                # Simulate fetching a row from the database
                return (b'existing_item_id_bytes',)  # Return mock data

            # Assign the fetchone coroutine function to the fetchone attribute of the cursor
            cursor_mock.fetchone = fetchone_coro

            # Return the cursor mock
            return cursor_mock

        # Assign the cursor coroutine function to the cursor attribute of the connection
        conn_mock.cursor = cursor_coro

        # Return the connection mock
        return conn_mock

    async def release_coro(conn):
        pass

    # Patch the aiomysql.Pool methods
    db_pool_mock.acquire = AsyncMock(side_effect=acquire_coro)
    db_pool_mock.release = AsyncMock(side_effect=release_coro)

    # Call the function under test
    result = await insert_item(item, db_pool_mock)

   # Assert the result
    expected_id = "existing_item_id_bytes"
    assert result['id'].strip("b'") == expected_id.encode().hex()


@pytest.mark.asyncio
async def test_get_items_within_date_range():
    # Mock the database pool
    db_pool_mock = MagicMock()

    # Mock the connection and cursor
    conn_mock = AsyncMock()
    cursor_mock = AsyncMock()

    # Define the list of items to be returned by fetchall
    items = [
        {'id': 'item_id_1', 'name': 'Item 1', 'category': 'Gift', 'price': '10.00'},
        {'id': 'item_id_2', 'name': 'Item 2', 'category': 'Gift', 'price': '20.00'}
    ]

    # Define the expected result
    expected_result = {
        "items": items,
        "total_price": 30.00
    }

    # Mock the execute method of the cursor
    cursor_mock.execute = AsyncMock()

    # Patch the fetchall method of the cursor to return the list of items
    cursor_mock.fetchall = AsyncMock(return_value=items)

    # Patch the __aenter__ method of the cursor to return the cursor mock
    conn_mock.cursor.return_value.__aenter__.return_value = cursor_mock

    # Patch the acquire method of the pool to return the connection mock
    db_pool_mock.acquire.return_value.__aenter__.return_value = conn_mock

    # Call the function under test
    result = await get_items_within_date_range(DateRangeInput(dt_from=datetime(2023, 1, 1),
                                                             dt_to=datetime(2023, 1, 2)),
                                               db_pool_mock)

    # Assert the result
    assert result == expected_result


@pytest.mark.asyncio
async def test_get_items_within_date_range_negative():
    # Mock the database pool
    mock_db_pool = MagicMock()

    # Set up a date range that does not contain any items
    date_range = DateRangeInput(dt_from=datetime(2022, 1, 1), dt_to=datetime(2022, 1, 5))

    # Mock the behavior of executing a query that returns no items
    mock_cursor = AsyncMock()
    mock_cursor.fetchall.return_value = []
    mock_db_pool.acquire.return_value.__aenter__.return_value.cursor.return_value.__aenter__.return_value = mock_cursor

    # Call the function under test
    result = await get_items_within_date_range(date_range, mock_db_pool)

    # Assert that the result is as expected
    assert result == {"message": "No items found within the specified date range"}