import os
import subprocess
from config.settings import OUTPUT_DIR

def convert_doc_to_docx(input_file):
    """
    Converts a .doc file to .docx using LibreOffice.
    
    :param input_file: Path to the .doc file.
    :return: Path to the converted .docx file or None if conversion fails.
    """
    if not input_file.lower().endswith(".doc"):
        raise ValueError("Invalid file format. Only .doc files are supported.")

    output_file = os.path.join(OUTPUT_DIR, os.path.basename(input_file).replace(".doc", ".docx"))

    try:
        subprocess.run(["libreoffice", "--headless", "--convert-to", "docx", "--outdir", OUTPUT_DIR, input_file], check=True)
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"Error converting {input_file} to DOCX: {e}")
        return None
