from PIL import Image
import pytesseract
import time
import os
import io
import logging
from PIL import Image
from io import BytesIO
import fitz  # PyMuPDF

# def process_image(image_path):
#     """Process the image and return the extracted text."""
#     image = Image.open(image_path)
#     text = pytesseract.image_to_string(image)
#     return text


def extract_and_combine_images(pdf_path):
    start_time = time.time()
    # Extract the base name of the PDF (without extension)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    input_dir = os.path.dirname(pdf_path)  # Directory where the PDF is located
    output_path = os.path.join(input_dir, f"{base_name}.jpg")
    
    if os.path.exists(output_path):
        logging.info(f"Combined image already exists for {pdf_path}: {output_path}")
        return output_path 
    
    pdf = fitz.open(pdf_path)
    all_images = []  # List to store extracted images

    for page_number in range(len(pdf)):
        page = pdf[page_number]
        images = page.get_images(full=True)

        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = pdf.extract_image(xref)
            image_bytes = base_image["image"]

            # Convert image bytes to PIL Image object
            image = Image.open(io.BytesIO(image_bytes))
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

        # Save the combined image in the same directory as the input PDF
        output_path = os.path.join(input_dir, f"{base_name}.jpg")
        combined_image.save(output_path)
        print(f"Combined image saved at: {output_path}")
        logging.info(f"Extracted and combined images from PDF in {time.time() - start_time:.2f} seconds.")
        return output_path  # Return the path of the combined image
    else:
        print(f"No images found in {pdf_path}.")
        return None
