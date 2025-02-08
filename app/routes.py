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

@routes.route('/process_pdf', methods=['POST'])
def process_pdf():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    file_path = os.path.join(INPUT_DIR, file.filename)
    file.save(file_path)

    extracted_info = file_processor.process_pdf_files(file.filename)
    return jsonify({"extracted_info": extracted_info})
