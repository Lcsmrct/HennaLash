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
    # Users indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("id", unique=True)
    
    # Appointments indexes
    await db.appointments.create_index("user_id")
    await db.appointments.create_index("slot_id")
    await db.appointments.create_index("status")
    await db.appointments.create_index("id", unique=True)
    
    # Time slots indexes
    await db.time_slots.create_index("date")
    await db.time_slots.create_index("is_available")
    await db.time_slots.create_index("id", unique=True)
    
    # Reviews indexes - optimized for faster queries
    await db.reviews.create_index("user_id")
    await db.reviews.create_index("status")
    await db.reviews.create_index("id", unique=True)
    await db.reviews.create_index([("status", 1), ("created_at", -1)])  # Compound index for approved reviews sorted by date
    await db.reviews.create_index("created_at", direction=-1)  # For sorting by most recent