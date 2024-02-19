import aiomysql

# Database configuration
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 3306,  # Default MySQL port
    "user": "db_app_user",
    "password": "admin_user",
    "db": "inventory",
}

async def create_db_pool():
    print("DEBUG: Creating database pool")
    pool = await aiomysql.create_pool(**DATABASE_CONFIG)
    return pool


async def close_db_pool(pool: aiomysql.Pool):
    pool.close()
    await pool.wait_closed()