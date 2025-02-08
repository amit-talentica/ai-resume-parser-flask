import os
import time
import subprocess
import logging
from PIL import Image
from io import BytesIO
from zipfile import ZipFile
from config.settings import OUTPUT_DIR
import platform

if platform.system() == "Windows":
    try:
        from win32com.client import Dispatch
    except ImportError:
        print("pywin32 is not installed. Install it using: pip install pywin32")


def convert_doc_to_docx(doc_path):
        """ Convert a .doc file to .docx using MS Word (Windows) or LibreOffice (Linux/Mac). """
        if not os.path.exists(doc_path):
            print(f"ERROR: File not found: {doc_path}")
            return None

        # Extract the directory of the .doc file and construct the .docx file path in the same directory
        doc_dir = os.path.dirname(doc_path)
        docx_path = os.path.join(doc_dir, os.path.basename(doc_path).replace(".doc", ".docx"))
        if os.name == "nt":  # Windows
            try:
                print(f" Converting {doc_path} to {docx_path} using MS Word...")
                word = Dispatch("Word.Application")
                word.Visible = False  # Background execution
                doc = word.Documents.Open(os.path.abspath(doc_path))
                doc.SaveAs(os.path.abspath(docx_path), FileFormat=16)  # Convert to .docx
                doc.Close()
                word.Quit()
                print(f"Conversion successful: {docx_path}")
                return docx_path
            except Exception as e:
                print(f"ERROR: Failed to convert {doc_path} - {e}")
                return None
                
        elif os.name == "posix":  # Linux/macOS
            try:
                print(f" Converting {doc_path} using LibreOffice...")
                subprocess.run(["libreoffice", "--headless", "--convert-to", "docx", doc_path], check=True)
                return docx_path if os.path.exists(docx_path) else None
            except Exception as e:
                print(f"ERROR: LibreOffice conversion failed for {doc_path} - {e}")
                return None
        else:
            print(f"Unsupported OS: {os.name}")

def extract_and_combine_images_from_docx(docx_path):
        # Extract the base name of the DOCX (without extension)
        start_time = time.time()
        base_name = os.path.splitext(os.path.basename(docx_path))[0]
        input_dir = os.path.dirname(docx_path)  # Directory where the DOCX is located
        output_path = os.path.join(input_dir, f"{base_name}.jpg")
        
        # Check if combined image already exists
        if os.path.exists(output_path):
            logging.info(f"Combined image already exists for {docx_path}: {output_path}")
            return output_path  # Return the path of the existing combined image

        # Open the DOCX file as a zip archive
        with ZipFile(docx_path, 'r') as docx_zip:
            image_files = [f for f in docx_zip.namelist() if f.startswith('word/media/')]
            
            # Extract all images
            all_images = []
            for image_file in image_files:
                image_data = docx_zip.read(image_file)
                image = Image.open(BytesIO(image_data))
                all_images.append(image)

        # Combine all images into one
        if all_images:
            # Determine the size of the combined image
            widths, heights = zip(*(img.size for img in all_images))
            total_width = max(widths)
            total_height = sum(heights)

            # Create a blank canvas
            combined_image = Image.new("RGB", (total_width, total_height))

            # Paste images on the canvas
            y_offset = 0
            for img in all_images:
                combined_image.paste(img, (0, y_offset))
                y_offset += img.height

            # Save the combined image in the same directory as the input DOCX
            combined_image.save(output_path)
            logging.info(f"Combined image saved at: {output_path}")
            logging.info(f"Extracted and combined images from DOCX in {time.time() - start_time:.2f} seconds.")

            return output_path  # Return the path of the combined image
        else:
            logging.warning(f"No images found in {docx_path}.")
            return None
