import os
import certifi
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv("backend/.env")
MONGODB_URI = os.getenv("MONGODB_URI")
print(f"Connecting to: {MONGODB_URI}")

async def test_conn():
    client = AsyncIOMotorClient(MONGODB_URI, tlsCAFile=certifi.where())
    try:
        info = await client.server_info()
        print("Success:", info)
    except Exception as e:
        print("Error:", e)

asyncio.run(test_conn())
