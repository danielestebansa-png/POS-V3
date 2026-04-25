import sys
import asyncio
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://postgres:mtERpauHwyIxYQaIkpDpbkSoZruYHdAh@postgres.railway.internal:5432/railway"

async def migrate():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE inventario ADD COLUMN IF NOT EXISTS stock NUMERIC(15,3) DEFAULT 0"))
            conn.commit()
            print("SUCCESS: Column added!")
        except Exception as e:
            print(f"ERROR: {e}")

asyncio.run(migrate())
