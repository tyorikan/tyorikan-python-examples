import os

from flask import Flask, request, send_from_directory
from google.cloud import storage

app = Flask(__name__)


@app.route("/download")
def download_object():
    """
    Downloads an object from Cloud Storage based on the provided path.

    Args:
        path: The path to the object in Cloud Storage, in the format {bucket}/{object_path}.

    Returns:
        The downloaded object as a file-like object.
    """

    path = request.args.get("path")
    if not path:
        return "Missing path query parameter", 400

    # Split the path into bucket and object name
    bucket_name, object_name = path.split("/", 1)
    filename = os.path.basename(path)

    # Create a Cloud Storage client
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(object_name)

    # Download the object
    try:
        blob.download_to_filename(filename)
        return send_from_directory(".", filename, as_attachment=True)
    except Exception as e:
        return f"Error downloading object: {e}", 500


if __name__ == "__main__":
    app.run(debug=True)
