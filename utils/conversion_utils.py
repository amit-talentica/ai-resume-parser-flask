import os
import time
import subprocess
import logging
from PIL import Image
from io import BytesIO
from zipfile import ZipFile
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
