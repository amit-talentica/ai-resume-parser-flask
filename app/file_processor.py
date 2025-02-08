import os
import logging
import base64
import pdfplumber
import fitz
import io
import time
from PIL import Image
from zipfile import ZipFile
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from utils.file_utils import write_output_file
from utils.image_utils import extract_and_combine_images

class FileProcessor:
    def __init__(self, input_directory, output_directory, client, system_prompt, user_prompt, json_template):
        self.input_directory = input_directory
        self.output_directory = output_directory
        self.client = client
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.json_template = json_template

    def convert_pdf_to_images(self, pdf_path):
        images = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                try:
                    images.append(page.to_image(resolution=300).original)
                except Exception as e:
                    logging.error(f"Error extracting image from PDF page: {str(e)}")
        return images

    def encode_image_to_base64(self, image_path):
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            logging.error(f"Error encoding image to base64: {str(e)}")
            return None

    # def process_pdf_file(self, pdf_file):
    #     start_time = time.time()
    #     pdf_path = os.path.join(self.input_directory, pdf_file)
    #     try:
    #         pdf_loader = PyPDFLoader(pdf_path)
    #         pdf_text = "".join(page.page_content for page in pdf_loader.load())

    #         if not pdf_text.strip():
    #             combined_image_path = extract_and_combine_images(pdf_path)
    #             if combined_image_path:
    #                 base64_image = self.encode_image_to_base64(combined_image_path)
    #                 pdf_text = self.client.call_gpt4o(base64_image)

    #         resume_info = self.client.extract_resume_info(pdf_text)
    #         write_output_file(self.output_directory, pdf_file, resume_info)
    #         logging.info(f"Processed PDF file {pdf_file} in {time.time() - start_time:.2f} seconds.")
    #     except Exception as e:
    #             logging.error(f"Error processing PDF {pdf_file}: {str(e)}")

    def process_pdf_files(self, pdf_file):

        start_time = time.time()
        pdf_file_path = os.path.join(self.input_directory, pdf_file)
        try:
            pdf_loader = PyPDFLoader(pdf_file_path)
            pdf_text = "".join(page.page_content for page in pdf_loader.load())

            # Check if extracted text is empty
            if not pdf_text.strip():
                logging.warning(f"Empty text extracted from {pdf_file}, processing images instead.,")
                combined_image_path = extract_and_combine_images(pdf_file_path)
                # Process combined image
                if combined_image_path and os.path.exists(combined_image_path):
                    base64_image = self.encode_image_to_base64(combined_image_path)
                    pdf_text = self.client.call_gpt4o(base64_image)

            resume_info = self.client.extract_resume_info(
                    pdf_text
                )

            write_output_file(self.output_directory, pdf_file, resume_info)
            logging.info(f"Processed PDF file {pdf_file} in {time.time() - start_time:.2f} seconds.")

        except Exception as e:
                logging.error(f"Error processing PDF {pdf_file}: {str(e)}")



