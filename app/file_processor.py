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



    def process_pdf_files(self, pdf_file):
        """
        Processes a PDF file: extracts text using PyPDFLoader, or processes images if text is empty.
        Extracted data is processed and saved to the output directory.

        :param pdf_file: Name of the PDF file to process.
        """
        start_time = time.time()
        pdf_file_path = os.path.join(self.input_directory, pdf_file)

        try:
            if not os.path.exists(pdf_file_path):
                logging.error(f"File not found: {pdf_file_path}")
                return

            logging.info(f"Processing PDF file: {pdf_file}")

            # Attempt text extraction
            try:
                pdf_loader = PyPDFLoader(pdf_file_path)
                pdf_text = "".join(page.page_content for page in pdf_loader.load())
            except Exception as e:
                logging.error(f"Error extracting text from {pdf_file}: {str(e)}")
                return

            # Check if extracted text is empty
            if not pdf_text.strip():
                logging.warning(f"Empty text extracted from {pdf_file}, attempting image extraction.")

                try:
                    combined_image_path = extract_and_combine_images(pdf_file_path)
                    if combined_image_path and os.path.exists(combined_image_path):
                        base64_image = self.encode_image_to_base64(combined_image_path)
                        pdf_text = self.client.call_gpt4o(base64_image)
                    else:
                        logging.error(f"Image extraction failed for {pdf_file}")
                        return
                except Exception as e:
                    logging.error(f"Error processing images from {pdf_file}: {str(e)}")
                    return

            # Extract structured information from text
            try:
                resume_info = self.client.extract_resume_info(pdf_text)
            except Exception as e:
                logging.error(f"Error extracting resume info from {pdf_file}: {str(e)}")
                return

            # Save output
            try:
                write_output_file(self.output_directory, pdf_file, resume_info)
                logging.info(f"Successfully processed PDF file {pdf_file} in {time.time() - start_time:.2f} seconds.")
            except Exception as e:
                logging.error(f"Error writing output for {pdf_file}: {str(e)}")

        except Exception as e:
            logging.critical(f"Unexpected error processing {pdf_file}: {str(e)}", exc_info=True)


    def process_image_files(self, image_file):
        """
        Processes an image file: Converts it to base64, extracts text using GPT-4o, 
        and saves the output to a file.

        :param image_file: Name of the image file to process.
        :return: Extracted text from the image or None if an error occurs.
        """
        start_time = time.time()
        image_file_path = os.path.join(self.input_directory, image_file)

        try:
            if not os.path.exists(image_file_path):
                logging.error(f"Image file not found: {image_file_path}")
                return None

            # Encode image to Base64
            try:
                base64_image = self.encode_image_to_base64(image_file_path)
                if not base64_image:
                    logging.error(f"Failed to encode image: {image_file_path}")
                    return None
            except Exception as e:
                logging.error(f"Error encoding image {image_file_path}: {str(e)}")
                return None

            # Call GPT-4o to extract text
            try:
                extracted_text = self.client.call_gpt4o(base64_image)
                if not extracted_text:
                    logging.warning(f"GPT-4o returned empty text for {image_file_path}")
                    return None
            except Exception as e:
                logging.error(f"Error extracting text from image {image_file_path} using GPT-4o: {str(e)}")
                return None

            # Save output to a file
            try:
                write_output_file(self.output_directory, image_file, extracted_text)
                logging.info(f"Successfully processed and saved output for {image_file} in {time.time() - start_time:.2f} seconds.")
            except Exception as e:
                logging.error(f"Error writing output file for {image_file}: {str(e)}")
                return None

            return extracted_text

        except Exception as e:
            logging.critical(f"Unexpected error processing image file {image_file_path}: {str(e)}", exc_info=True)
            return None




