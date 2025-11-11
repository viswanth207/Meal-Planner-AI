import os
import logging
from pymongo import MongoClient
from pymongo import ASCENDING
from app.config import MONGODB_URI

logger = logging.getLogger(__name__)

# Build a resilient URI for serverless environments. Avoid crashing on bad/missing URIs.
_env_has_mongo = bool(os.getenv("MONGODB_URI") or os.getenv("MONGO_URI"))
_is_vercel = os.getenv("VERCEL") == "1"
_uri = MONGODB_URI
if _is_vercel and not _env_has_mongo:
    # Use a non-connecting local fallback to allow app import/startup
    _uri = "mongodb://127.0.0.1:27017/?connect=false"

try:
    client = MongoClient(_uri, serverSelectionTimeoutMS=1000)
except Exception as e:
    # Last-resort fallback: ensure client object exists even if URI is malformed
    logger.warning(f"MongoClient init failed for URI '{_uri}': {e}. Using safe local fallback.")
    client = MongoClient("mongodb://127.0.0.1:27017/?connect=false", serverSelectionTimeoutMS=1000)

db = client.recipe_planner  # Explicitly specify database name

users_col = db['users']
ingredients_col = db['ingredients']
mealplans_col = db['meal_plans']


def init_indexes():
    """Create indexes to improve query performance. Safe to call multiple times."""
    try:
        # Verify connectivity quickly; skip index creation if unreachable
        try:
            client.server_info()
        except Exception:
            return
        # Users: fast lookup by email (case normalized to lowercase at signup)
        users_col.create_index([("email", ASCENDING)], name="idx_users_email")
    except Exception:
        pass
    try:
        # Ingredients: speed up per-user queries and updates by name
        ingredients_col.create_index([("user_id", ASCENDING), ("name", ASCENDING)], name="idx_ingredients_user_name")
    except Exception:
        pass
    try:
        # Meal plans: support scheduler lookups and daily idempotency
        mealplans_col.create_index([("user_id", ASCENDING), ("date", ASCENDING)], name="idx_mealplans_user_date")
        mealplans_col.create_index([("created_at", ASCENDING)], name="idx_mealplans_created_at")
    except Exception:
        pass
