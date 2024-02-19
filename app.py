from fastapi import FastAPI, Query, HTTPException, Depends
import aiomysql
from database_operations.models import ItemResponse, DateRangeInput, CategoryInput
from database_operations.database import create_db_pool

app = FastAPI()

# Configure logging settings
import logging

logging.basicConfig(level=logging.DEBUG)  # Set logging level to DEBUG
logger = logging.getLogger(__name__)

@app.post("/items/", response_model=ItemResponse)
async def create_item(item: dict, db_pool: aiomysql.Pool = Depends(create_db_pool)):
    try:
        logger.debug("Creating item: %s", item)
        async with db_pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("INSERT INTO items ...")  # Your insert query here
                # Commit the transaction if necessary
        return item
    except aiomysql.MySQLError as e:
        logger.error("Database error occurred: %s", e)
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.error("An error occurred: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/items/")
async def query_items_within_date_range(date_range: DateRangeInput, db_pool: aiomysql.Pool = Depends(create_db_pool)):
    try:
        async with db_pool.acquire() as conn:
            async with conn.cursor(aiomysql.cursors.DictCursor) as cursor:
                await cursor.execute("SELECT * FROM items WHERE ...")  # Your query here
                items_data = await cursor.fetchall()
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

                if not items:
                    raise HTTPException(status_code=404, detail=f"No items found for category: {category}")

                return {"items": items}

    except aiomysql.MySQLError as e:
        logger.error("Database error occurred: %s", e)
        raise HTTPException(status_code=500, detail="Database error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
