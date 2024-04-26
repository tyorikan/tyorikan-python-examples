# Import the Google Cloud client library
from google.cloud import storage
import sqlalchemy

# Import the PostgreSQL client library
import psycopg2

# Import the CSV reader library
import csv, os

# Instantiate a client
storage_client = storage.Client()

# Download the CSV file from Cloud Storage
bucket_name = "your-bucket-name"
source_blob_name = "your-csv-file-name.csv"
destination_file_name = "/tmp/your-csv-file-name.csv"

bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(source_blob_name)
blob.download_to_filename(destination_file_name)

# Connect to the AlloyDB (PostgreSQL) instance
# Note: Saving credentials in environment variables is convenient, but not
# secure - consider a more secure solution such as
# Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
# keep secrets safe.
db_host = os.environ["INSTANCE_HOST"]  # e.g. '127.0.0.1' ('172.17.0.1' if deployed to GAE Flex)
db_user = os.environ["DB_USER"]  # e.g. 'my-db-user'
db_pass = os.environ["DB_PASS"]  # e.g. 'my-db-password'
db_name = os.environ["DB_NAME"]  # e.g. 'my-database'
db_port = os.environ["DB_PORT"]  # e.g. 5432

# Construct the connection string
connection_string = (
    "postgresql+pg8000://{}:{}@{}:{}/{}".format(
        db_user, db_pass, db_host, db_port, db_name
    )
)

# Create the engine
engine = sqlalchemy.create_engine(connection_string)

# Create the table
table_name = "your_table_name"

# Import the CSV file into the table
with open(destination_file_name, "r") as f:
    reader = csv.reader(f)
    next(reader)  # Skip the header row
    for row in reader:
        engine.execute(
            "INSERT INTO {} (name, age) VALUES ('{}', {})".format(
                table_name, row[0], row[1]
            )
        )

# Print the results
results = engine.execute("SELECT * FROM {}".format(table_name))
for row in results:
    print(row)  
