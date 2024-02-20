import aiomysql
import logging
from fastapi import FastAPI, Query, HTTPException, Depends
from database_operations.crud import insert_item, get_items_within_date_range
from database_operations.models import ItemResponse, DateRangeInput, CategoryInput
from database_operations.database import create_db_pool

app = FastAPI()

# Configure logging settings
logging.basicConfig(level=logging.DEBUG)  # Set logging level to DEBUG
logger = logging.getLogger(__name__)

@app.post("/items/", response_model=ItemResponse)
async def create_item(item: dict, db_pool: aiomysql.Pool = Depends(create_db_pool)):
    try:
        logger.debug("Creating item: %s", item)
        created_item = await insert_item(item, db_pool)
        return created_item
    except aiomysql.MySQLError as e:
        logger.error("Database error occurred: %s", e)
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.error("An error occurred: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/items/")
async def query_items_within_date_range(date_range: DateRangeInput, db_pool: aiomysql.Pool = Depends(create_db_pool)):
    try:
        items_data = await get_items_within_date_range(date_range, db_pool)
        return items_data
    except aiomysql.MySQLError as e:
        logger.error("Database error occurred: %s", e)
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.error("An error occurred: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/items-by-category/")
async def query_items_by_category(
    category_input: CategoryInput = None,
    category: str = Query(None),
    db_pool: aiomysql.Pool = Depends(create_db_pool)
):
    try:
        if category_input is not None:
            category = category_input.category.lower()

        logger.debug("Before acquiring database connection")

        async with db_pool.acquire() as conn:
            async with conn.cursor(aiomysql.cursors.DictCursor) as cursor:
                logger.debug("Database connection acquired")
                if category == "all":
                    query = "SELECT category, SUM(price) AS total_price, ROW_NUMBER() OVER () AS count FROM items GROUP BY category"
                    params = ()
                else:
                    query = "SELECT category, SUM(price) AS total_price, ROW_NUMBER() OVER () AS count FROM items WHERE category = %s GROUP BY category"
                    params = (category,)

                await cursor.execute(query, params)
                items = await cursor.fetchall()

                return {"items": items} if items else {"message": f"No items found for category: {category}"}

    except aiomysql.MySQLError as e:
        logger.error("Database error occurred: %s", e)
        raise HTTPException(status_code=500, detail="Database error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
