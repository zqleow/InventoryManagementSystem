import pytest
import httpx
import database_operations
from unittest.mock import MagicMock, AsyncMock
from database_operations.models import CategoryInput
from fastapi import HTTPException

from app import app, query_items_by_category
from database_operations.database import create_db_pool

@pytest.mark.asyncio
async def test_query_items_by_category_database_operation():
    # Mock the category input
    category_input = CategoryInput(category="all")
    
    # Mock the expected items
    expected_items = [
        {"category": "Gift", "total_price": 25.0, "count": 1},
        {"category": "Stationary", "total_price": 10.5, "count": 2}
    ]
    
    # Create a real aiomysql.Pool instance
    db_pool = await create_db_pool()
    
    try:
        items = await query_items_by_category(category_input=category_input, db_pool=db_pool)
        assert items is not None  # Ensure that items are retrieved successfully
    except HTTPException as e:
        raise AssertionError(f"Query items by category failed with HTTP status code {e.status_code}: {e.detail}")

@pytest.mark.asyncio
async def test_query_items_by_category_all(monkeypatch):
    # Mock the db_pool object
    mock_db_pool = AsyncMock()

    # Patch create_db_pool in the database_operations.database module
    monkeypatch.setattr("database_operations.database.create_db_pool", MagicMock(return_value=mock_db_pool))

    # Make the request to the endpoint
    category_data = {"category": "all"}
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/items-by-category/", params=category_data)

    # Assertions...
    assert response.status_code == 200

    json_data = response.json()
    expected_items = json_data['items']

    assert expected_items
    print("Expected items:", expected_items)

    # Verify patching
    print("Patched create_db_pool:", database_operations.database.create_db_pool)

@pytest.mark.asyncio
async def test_query_items_by_specific_category_with_httpx(monkeypatch):
    # Mock the db_pool object
    mock_db_pool = AsyncMock()

    # Patch create_db_pool in the database_operations.database module
    monkeypatch.setattr("database_operations.database.create_db_pool", MagicMock(return_value=mock_db_pool))

    # Specify a valid category
    category_input = CategoryInput(category="Stationary")

    # Mock the expected items for the "Stationary" category
    expected_items = [{"category": "Stationary", "total_price": 10.5, "count": 1}]

    # Mock the database query result to return the expected items for the "Stationary" category
    mock_cursor = AsyncMock()
    mock_cursor.fetchall.return_value = expected_items
    mock_conn = AsyncMock()
    mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
    mock_db_pool.acquire.return_value.__aenter__.return_value = mock_conn

    # Make the request to the endpoint
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/items-by-category/", params={"category": category_input.category})

    # Assertions
    assert response.status_code == 200
    json_data = response.json()
    assert "items" in json_data

    # Check that the returned items match the expected items
    assert json_data['items'] == expected_items

@pytest.mark.asyncio
async def test_query_items_by_category_not_found(monkeypatch):
    # Mock the db_pool object
    mock_db_pool = AsyncMock()

    # Patch create_db_pool in the database_operations.database module
    monkeypatch.setattr("database_operations.database.create_db_pool", MagicMock(return_value=mock_db_pool))

    # Mock the category input
    category_input = CategoryInput(category="NonExistentCategory")

    # Mock the database query result to return an empty list
    mock_cursor = AsyncMock()
    mock_cursor.fetchall.return_value = []
    mock_conn = AsyncMock()
    mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
    mock_db_pool.acquire.return_value.__aenter__.return_value = mock_conn

    # Make the request to the endpoint
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/items-by-category/", params={"category": category_input.category})

    # Assertions
    assert response.status_code == 200
    json_data = response.json()
    assert json_data['message'] == "No items found for category: NonExistentCategory"
