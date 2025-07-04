from flask import Blueprint, request, jsonify, send_file
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
import zipfile
import io
import tempfile
from backend_filepro import FileHandler  # Assuming FileHandler is defined in backend_filepro.py
from db import ChunkDatabase

# Load environment variables from .env file
load_dotenv()

cloud_routes = Blueprint('routes', __name__)

# Retrieve environment variables
account_name = os.getenv("ACCOUNT_NAME")
account_key = os.getenv("ACCOUNT_KEY")
container_name = os.getenv("CONTAINER_NAME")

if not account_name or not account_key or not container_name:
    raise ValueError("Missing required environment variables: ACCOUNT_NAME, ACCOUNT_KEY, or CONTAINER_NAME")

# Create the BlobServiceClient using the storage account key
blob_service_client = BlobServiceClient(
    f"https://{account_name}.blob.core.windows.net",
    credential=account_key
)


@cloud_routes.route('/upload-multiple', methods=['POST'])
def upload_multiple_route():
    try:
        uploaded_files = request.files.getlist("files")
        print(f"Uploaded files: {uploaded_files}")
        if not uploaded_files:
            return jsonify({"error": "No files provided"}), 400

        temp_file_paths = []
        original_filenames = []

        for file in uploaded_files:
            original_filename = file.filename
            original_filenames.append(original_filename)  # Store original filename
            filename = secure_filename(original_filename)

            # Save locally to a temp file first
            file_ext = os.path.splitext(filename)[1] if filename else ''
            temp = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
            file.save(temp.name)
            temp_file_paths.append(temp.name)

            # Then upload that saved file to Azure
            with open(temp.name, "rb") as data:
                blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)
                print(f"Uploading file: {filename} to container: {container_name}")
                blob_client.upload_blob(data, overwrite=True)

        # Use singleton instance and initialize with file paths
        handler = FileHandler()
        handler.initialize(temp_file_paths)
        handler.set_actual_names(original_filenames)  # Pass original filenames

        # # Optional: Process files here
        # results = handler.process_all_files()
        # print("Processed results:", results)

        return jsonify({"message": "Files uploaded and processed successfully"}), 200

    except Exception as e:
        print(f"Error during file upload: {str(e)}")
        return jsonify({"error": str(e)}), 500


@cloud_routes.route('/download-multiple', methods=['POST'])
def download_multiple_route():
    try:
        data = request.get_json()
        files = data.get('files', [])  # List of blob names
        project_name = data.get("project_name")

        db = ChunkDatabase()
        keywords = db.get_all_retrieved_keywords_by_project(project_name)
        files = db.get_files_with_keywords(keywords, project_name)

        if not files:
            return jsonify({"error": "No files provided"}), 400

        # Create in-memory ZIP archive
        from werkzeug.utils import secure_filename

        ...

        # Create in-memory ZIP archive
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            for file_name in files:
                blob_name = secure_filename(file_name)  # sanitize to match blob name
                blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
                blob_data = blob_client.download_blob().readall()
                zf.writestr(file_name, blob_data)  # keep original name inside the ZIP
        memory_file.seek(0)

        return send_file(
            memory_file,
            download_name='files.zip',
            as_attachment=True,
            mimetype='application/zip'
        )
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400  # Custom error from DB function

    except Exception as e:
        return jsonify({"error": str(e)}), 500