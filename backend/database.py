from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance."""
    return db

async def close_db_connection():
    """Close database connection."""
    client.close()

# Initialize indexes for better performance
async def create_indexes():
    """Create database indexes for better performance."""
    try:
        # Users indexes - optimized
        await db.users.create_index("email", unique=True)
        await db.users.create_index("id", unique=True)
        await db.users.create_index("role")  # For admin queries
        
        # Appointments indexes - optimized compound indexes
        await db.appointments.create_index("user_id")
        await db.appointments.create_index("slot_id")
        await db.appointments.create_index("status")
        await db.appointments.create_index("id", unique=True)
        await db.appointments.create_index([("created_at", -1)])  # For sorting by most recent
        await db.appointments.create_index([("user_id", 1), ("created_at", -1)])  # User's appointments sorted
        await db.appointments.create_index([("status", 1), ("created_at", -1)])  # Status queries sorted
        
        # Time slots indexes - optimized for availability queries
        await db.time_slots.create_index("date")
        await db.time_slots.create_index("is_available")
        await db.time_slots.create_index("id", unique=True)
        await db.time_slots.create_index([("is_available", 1), ("date", 1)])  # Available slots by date
        await db.time_slots.create_index([("date", 1), ("start_time", 1)])  # Chronological ordering
        
        # Reviews indexes - optimized for public and admin queries
        await db.reviews.create_index("user_id")
        await db.reviews.create_index("status")
        await db.reviews.create_index("id", unique=True)
        await db.reviews.create_index([("status", 1), ("created_at", -1)])  # Approved reviews sorted by date (most used)
        await db.reviews.create_index([("created_at", -1)])  # For admin panel sorting
        await db.reviews.create_index([("rating", -1), ("created_at", -1)])  # For rating-based queries
        
        print("✅ Database indexes created successfully")
    except Exception as e:
        print(f"❌ Error creating indexes: {e}")