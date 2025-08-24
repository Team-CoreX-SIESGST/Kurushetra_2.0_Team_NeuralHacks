
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.settings import settings

client: AsyncIOMotorClient = None

async def connect_db():
    global client
    try:
        # Check if MongoDB URL is configured
        if not settings.mongodb_url or settings.mongodb_url.strip() == "":
            print("⚠️  MongoDB URL not configured, skipping database connection")
            return
            
        client = AsyncIOMotorClient(settings.mongodb_url)
        await client.server_info()
        print("✅ MongoDB connected successfully")
    except Exception as e:
        print(f"⚠️  MongoDB connection failed: {e}")
        print("⚠️  Continuing without database connection")
        # Don't raise the exception, just log it
        pass

def get_db() -> AsyncIOMotorDatabase:
    if client is None:
        # Return None for demo mode without MongoDB
        return None
    return client.get_database()
