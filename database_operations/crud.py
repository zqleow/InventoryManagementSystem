import aiomysql
import uuid
from .models import DateRangeInput

async def insert_item(item: dict, db_pool: aiomysql.Pool):
    conn = await db_pool.acquire()
    try:
        cursor = await conn.cursor()

        # Validate input data
        if not all(key in item for key in ('name', 'category', 'price')):
            raise ValueError("Item dictionary must contain 'name', 'category', and 'price' keys")

        # Check if an item with the same name already exists
        await cursor.execute(
            "SELECT id, price FROM items WHERE name = %s", (item['name'],)
        )
        existing_item = await cursor.fetchone()

        if existing_item:
            # Update existing item
            existing_item_id = existing_item[0]
            await cursor.execute(
                "UPDATE items SET category = %s, price = %s WHERE id = %s",
                (item["category"], "{:.2f}".format(float(item["price"])), existing_item_id)
            )
            await conn.commit()
            return {"id": existing_item_id.hex()}  # Convert bytes to hex string
        else:
            # Insert new item
            new_item_id = uuid.uuid4()
            new_item_id_bytes = new_item_id.bytes
            await cursor.execute(
                "INSERT INTO items (id, name, category, price) VALUES (%s, %s, %s, %s)",
                (new_item_id_bytes, item["name"], item["category"], "{:.2f}".format(float(item["price"])))
            )
            await conn.commit()
            return {"id": str(new_item_id)}
    except Exception as e:
        await conn.rollback()  # Rollback changes in case of error
        raise e
    finally:
        await db_pool.release(conn)

async def get_items_within_date_range(date_range: DateRangeInput, db_pool: aiomysql.Pool):
    async with db_pool.acquire() as conn:
        cursor = await conn.cursor(aiomysql.cursors.DictCursor)
        async with cursor as cursor:
            # Define the SQL query with parameters
            sql = "SELECT id, name, category, price FROM items WHERE last_updated_dt BETWEEN %s AND %s"

            # Execute the query with parameters
            await cursor.execute(sql, (date_range.dt_from, date_range.dt_to))
            items = await cursor.fetchall()

            if not items:
                return {"message": "No items found within the specified date range"}

            # Decode byte strings and convert bytes to UUID where necessary
            for item in items:
                for key, value in item.items():
                    if isinstance(value, bytes):
                        try:
                            # Attempt to decode byte string to UUID
                            item[key] = uuid.UUID(bytes=value)
                        except ValueError:
                            # Handle the exception by assigning a default or error message
                            item[key] = "Invalid encoding"

            # Calculate the total price of all items
            total_price = sum(float(item['price']) for item in items)

            return {"items": items, "total_price": total_price}
