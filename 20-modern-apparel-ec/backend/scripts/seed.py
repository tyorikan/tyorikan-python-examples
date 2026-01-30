import os
import uuid
from datetime import datetime
from google.cloud import spanner

PROJECT_ID = "test-project"
INSTANCE_ID = "test-instance"
DATABASE_ID = "test-database"

# Force Emulator usage for this script
os.environ["SPANNER_EMULATOR_HOST"] = "localhost:9010"
os.environ["GOOGLE_CLOUD_PROJECT"] = "test-project"

DATA = [
    {
        "category": "Men",
        "items": [
            {"name": "Ultra Stretch Chino Pants", "price": 4900, "desc": "Comfortable stretch fabric for daily urban life."},
            {"name": "Merino Wool V-Neck Sweater", "price": 3900, "desc": "Fine merino wool with a premium texture."},
            {"name": "Oxford Slim Fit Shirt", "price": 2900, "desc": "Classic silhouette made from high-quality cotton."},
            {"name": "Technical Parka", "price": 12800, "desc": "Water-repellent and windproof for outdoor performance."},
            {"name": "Seamless Down Coat", "price": 19900, "desc": "Ultimate warmth with a minimalist design."}
        ]
    },
    {
        "category": "Women",
        "items": [
            {"name": "Cashmere Crew Neck Sweater", "price": 9900, "desc": "100% cashmere for unrivaled softness."},
            {"name": "High Rise Wide Jeans", "price": 4900, "desc": "Modern silhouette with premium denim."},
            {"name": "Rayon Bow Tie Blouse", "price": 2900, "desc": "Elegant and easy-care for professional looks."},
            {"name": "Pleated Accordion Skirt", "price": 3900, "desc": "Dynamic movement with sharp pleats."},
            {"name": "Linen Blend Open Collar Shirt", "price": 2900, "desc": "Breathable and cool for summer days."}
        ]
    },
    {
        "category": "Accessories",
        "items": [
            {"name": "Leather Minimalist Wallet", "price": 5800, "desc": "Supple leather with a compact design."},
            {"name": "Tech Backpack Layer 1", "price": 8900, "desc": "Ergonomic design with laptop compartment."},
            {"name": "Cashmere Knit Scarf", "price": 4900, "desc": "Soft warmth for colder seasons."},
            {"name": "Urban Canvas Tote", "price": 1900, "desc": "Heavy-duty canvas for daily use."},
            {"name": "Modular Waist Bag", "price": 3500, "desc": "Versatile storage for city commuters."}
        ]
    }
]

COLORS = ["Black", "White", "Navy", "Beige", "Charcoal"]
SIZES = ["S", "M", "L", "XL"]

def seed_data():
    client = spanner.Client(project=PROJECT_ID)
    instance = client.instance(INSTANCE_ID)
    database = instance.database(DATABASE_ID)

    print(f"Seeding data to {DATABASE_ID}...")

    def insert_products(transaction):
        product_rows = []
        variant_rows = []
        
        for cat_data in DATA:
            category = cat_data["category"]
            for item in cat_data["items"]:
                p_id = str(uuid.uuid4())
                product_rows.append((
                    p_id,
                    item["name"],
                    item["desc"],
                    item["price"],
                    category,
                    datetime.utcnow()
                ))
                
                # Create 3-5 variants for each product
                for color in COLORS[:3]:  # First 3 colors
                    for size in SIZES[1:3]: # M, L
                        variant_rows.append((
                            p_id,
                            str(uuid.uuid4()),
                            color,
                            size,
                            100 # stock
                        ))

        transaction.insert(
            "Products",
            columns=("ProductId", "Name", "Description", "BasePrice", "CategoryId", "CreatedAt"),
            values=product_rows
        )
        transaction.insert(
            "ProductVariants",
            columns=("ProductId", "VariantId", "Color", "Size", "StockQuantity"),
            values=variant_rows
        )
        print(f"Inserted {len(product_rows)} products and {len(variant_rows)} variants.")

    database.run_in_transaction(insert_products)
    print("Seeding completed successfully.")

if __name__ == "__main__":
    seed_data()
