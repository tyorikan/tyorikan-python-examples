import os
import uuid
import json
from datetime import datetime
from google.cloud import spanner

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "test-project")
INSTANCE_ID = os.getenv("SPANNER_INSTANCE", "test-instance")
DATABASE_ID = os.getenv("SPANNER_DATABASE", "test-database")

# Force Emulator usage for this script if not set
if "SPANNER_EMULATOR_HOST" not in os.environ:
    os.environ["SPANNER_EMULATOR_HOST"] = "localhost:9010"

COLORS = ["Black", "White", "Navy", "Beige", "Charcoal"]
SIZES = ["S", "M", "L", "XL"]

def seed_data():
    client = spanner.Client(project=PROJECT_ID)
    instance = client.instance(INSTANCE_ID)
    database = instance.database(DATABASE_ID)

    # Load master data from JSON
    json_path = os.path.join(os.path.dirname(__file__), 'master_data.json')
    with open(json_path, 'r') as f:
        master_data = json.load(f)

    print(f"Seeding data to {DATABASE_ID} from {json_path}...")

    def upsert_products(transaction):
        product_rows = []
        variant_rows = []
        
        for cat_data in master_data:
            category = cat_data["category"]
            for item in cat_data["items"]:
                # Use a deterministic UUID based on name for idempotency if possible, 
                # but for this example we keep it simple or use upsert logic.
                # In a real scenario, ProductId might be fixed in the JSON.
                p_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, item["name"]))
                product_rows.append((
                    p_id,
                    item["name"],
                    item["desc"],
                    item["price"],
                    category,
                    datetime.utcnow()
                ))
                
                # Create variants
                for i, color in enumerate(COLORS[:3]):
                    for j, size in enumerate(SIZES[1:3]):
                        v_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{item['name']}-{color}-{size}"))
                        variant_rows.append((
                            p_id,
                            v_id,
                            color,
                            size,
                            100 # stock
                        ))

        transaction.insert_or_update(
            "Products",
            columns=("ProductId", "Name", "Description", "BasePrice", "CategoryId", "CreatedAt"),
            values=product_rows
        )
        transaction.insert_or_update(
            "ProductVariants",
            columns=("ProductId", "VariantId", "Color", "Size", "StockQuantity"),
            values=variant_rows
        )
        print(f"Upserted {len(product_rows)} products and {len(variant_rows)} variants.")

    database.run_in_transaction(upsert_products)
    print("Seeding completed successfully.")

if __name__ == "__main__":
    seed_data()
