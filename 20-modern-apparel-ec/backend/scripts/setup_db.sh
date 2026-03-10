#!/bin/bash
set -e

# Change to the directory where this script is located
cd "$(dirname "$0")"

echo "Applying DDL..."
python migrate.py

echo "Seeding master data..."
python seed.py

echo "Spanner setup completed successfully."
