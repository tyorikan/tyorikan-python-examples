from google.cloud import spanner
from functools import lru_cache
import os

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "test-project")
INSTANCE_ID = os.getenv("SPANNER_INSTANCE", "test-instance")
DATABASE_ID = os.getenv("SPANNER_DATABASE", "test-database")

@lru_cache()
def get_spanner_client():
    return spanner.Client(project=PROJECT_ID)

@lru_cache()
def get_instance():
    client = get_spanner_client()
    return client.instance(INSTANCE_ID)

@lru_cache()
def get_database():
    instance = get_instance()
    return instance.database(DATABASE_ID)

def init_spanner():
    """Check if we can connect to Spanner (Optional startup check)"""
    try:
        db = get_database()
        print(f"Connected to Spanner: {db.name}")
        return True
    except Exception as e:
        print(f"Failed to connect to Spanner: {e}")
        return False
