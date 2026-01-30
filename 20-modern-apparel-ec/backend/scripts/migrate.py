import os
import sys
from google.cloud import spanner
from google.api_core.exceptions import AlreadyExists

# Ensure backend directory is in path for imports if needed
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "test-project")
INSTANCE_ID = os.getenv("SPANNER_INSTANCE", "test-instance")
DATABASE_ID = os.getenv("SPANNER_DATABASE", "test-database")

def run_migration():
    print(f"Connecting to Spanner: {PROJECT_ID}/{INSTANCE_ID}")
    client = spanner.Client(project=PROJECT_ID)
    
    # Create Instance if not exists (Emulator only usually, or requires permissions)
    instance = client.instance(INSTANCE_ID)
    try:
        if not instance.exists():
            print(f"Creating instance {INSTANCE_ID}...")
            config_name = f"{client.project_name}/instanceConfigs/emulator-config"
            instance = client.instance(INSTANCE_ID, configuration_name=config_name)
            op = instance.create()
            op.result(120)  # Wait for creation
            print("Instance created.")
    except Exception as e:
        print(f"Warning: Instance creation skipped/failed: {e}")

    # Read DDL
    with open(os.path.join(os.path.dirname(__file__), '../ddl.sql'), 'r') as f:
        ddl_statements = f.read().split(';')
        # Clean up statements
        ddl_statements = [s.strip() for s in ddl_statements if s.strip()]

    # Create Database
    database = instance.database(DATABASE_ID, ddl_statements=ddl_statements)
    if not database.exists():
        print(f"Creating database {DATABASE_ID}...")
        try:
            op = database.create()
            op.result(120)
            print("Database created and schema applied.")
        except Exception as e:
             print(f"Error creating database: {e}")
    else:
        print(f"Database {DATABASE_ID} already exists. Skipping DDL application.")

if __name__ == "__main__":
    # Force Emulator usage for this script
    os.environ["SPANNER_EMULATOR_HOST"] = "localhost:9010"
    os.environ["GOOGLE_CLOUD_PROJECT"] = "test-project"
    
    # Reload constants after env set (in global scope)
    PROJECT_ID = "test-project"
    INSTANCE_ID = "test-instance"
    DATABASE_ID = "test-database"

    run_migration()
