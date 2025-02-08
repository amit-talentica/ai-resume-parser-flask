from flask import Blueprint, request, jsonify
import os
from app.file_processor import FileProcessor
from app.openai_client import OpenAIClient
from config.settings import OPENAI_API_KEY, INPUT_DIR, OUTPUT_DIR

routes = Blueprint("routes", __name__)

# Initialize OpenAI client
client = OpenAIClient(OPENAI_API_KEY)

# Initialize FileProcessor
file_processor = FileProcessor(INPUT_DIR, OUTPUT_DIR, client, "Your System Prompt", "Your User Prompt", "Your JSON Template")

@routes.route('/process_file', methods=['POST'])
def process_file():
    """
    Handles both PDF and image files, extracts relevant information, and returns the result.
    """
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    file_path = os.path.join(INPUT_DIR, file.filename)
    file.save(file_path)

    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension in [".pdf"]:
        extracted_info = file_processor.process_pdf_files(file.filename)
    elif file_extension in [".png", ".jpg", ".jpeg"]:
        extracted_info = file_processor.process_image_files(file.filename)
    elif file_extension in [".docx"]:
        extracted_info = file_processor.process_docx_files(file.filename)
    elif file_extension in [".doc"]:
        extracted_info = file_processor.process_doc_files(file.filename)
    else:
        return jsonify({"error": "Unsupported file format"}), 400

    return jsonify({"extracted_info": extracted_info})
