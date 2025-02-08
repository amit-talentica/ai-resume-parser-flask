import os
import logging
import base64
import pdfplumber
import time

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from utils.file_utils import write_output_file
from utils.image_utils import extract_and_combine_images
from utils.conversion_utils import extract_and_combine_images_from_docx,convert_doc_to_docx


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
                return {"error": f"File not found: {pdf_file}"}

            try:
                pdf_loader = PyPDFLoader(pdf_file_path)
                pdf_text = "".join(page.page_content for page in pdf_loader.load())
            except Exception as e:
                logging.error(f"Error reading PDF file {pdf_file}: {str(e)}")
                return {"error": f"Failed to read PDF file: {pdf_file}"}

            resume_info = None

            # If text is extracted successfully, process it
            if pdf_text.strip():
                try:
                    resume_info = self.client.extract_resume_info(pdf_text)
                except Exception as e:
                    logging.error(f"Error extracting resume info from text in {pdf_file}: {str(e)}")
                    return {"error": f"Failed to extract structured data from PDF text: {pdf_file}"}
            else:
                logging.warning(f"Empty text extracted from {pdf_file}, processing images instead.")
                
                try:
                    combined_image_path = extract_and_combine_images(pdf_file_path)
                    if not combined_image_path or not os.path.exists(combined_image_path):
                        logging.error(f"Failed to extract images from {pdf_file}")
                        return {"error": f"Failed to extract images from {pdf_file}"}

                    base64_image = self.encode_image_to_base64(combined_image_path)
                    resume_info = self.client.call_gpt4o(base64_image)

                    if not resume_info.strip():
                        logging.error(f"Failed to extract text from {pdf_file} even after image processing.")
                        return {"error": f"Text extraction failed for {pdf_file}, even from images."}

                except Exception as e:
                    logging.error(f"Error processing images for {pdf_file}: {str(e)}")
                    return {"error": f"Image processing failed for {pdf_file}"}

            # Save the extracted information
            try:
                write_output_file(self.output_directory, pdf_file, resume_info)
                logging.info(f"Processed PDF file {pdf_file} in {time.time() - start_time:.2f} seconds.")
                return {"message": f"Successfully processed {pdf_file}"}
            except Exception as e:
                logging.error(f"Error writing output for {pdf_file}: {str(e)}")
                return {"error": f"Failed to save extracted data for {pdf_file}"}

        except Exception as e:
            logging.error(f"Unexpected error processing PDF {pdf_file}: {str(e)}")
            return {"error": f"Unexpected error while processing {pdf_file}"}


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
                return {"message": f"Successfully processed {image_file}"}
            except Exception as e:
                logging.error(f"Error writing output file for {image_file}: {str(e)}")
                return None

        except Exception as e:
            logging.critical(f"Unexpected error processing image file {image_file_path}: {str(e)}", exc_info=True)
            return None
        

    def process_docx_files(self, docx_file):
        start_time = time.time()
        docx_file_path = os.path.join(self.input_directory, docx_file)

        try:
            if not os.path.exists(docx_file_path):
                logging.error(f"File not found: {docx_file_path}")
                return {"error": f"File not found: {docx_file}"}

            try:
                docx_loader = Docx2txtLoader(docx_file_path)
                docx_text = "".join(page.page_content for page in docx_loader.load())
            except Exception as e:
                logging.error(f"Error reading DOCX file {docx_file}: {str(e)}")
                return {"error": f"Failed to read DOCX file: {docx_file}"}

            resume_info = None

            # If text is extracted successfully, process it
            if docx_text.strip():
                try:
                    resume_info = self.client.extract_resume_info(docx_text)
                except Exception as e:
                    logging.error(f"Error extracting resume info from text in {docx_file}: {str(e)}")
                    return {"error": f"Failed to extract structured data from DOCX text: {docx_file}"}
            else:
                logging.warning(f"Empty text extracted from {docx_file}, processing images instead.")

                try:
                    combined_image_path = extract_and_combine_images_from_docx(docx_file_path)
                    if not combined_image_path or not os.path.exists(combined_image_path):
                        logging.error(f"Failed to extract images from {docx_file}")
                        return {"error": f"Failed to extract images from {docx_file}"}

                    base64_image = self.encode_image_to_base64(combined_image_path)
                    resume_info = self.client.call_gpt4o(base64_image)

                    if not resume_info.strip():
                        logging.error(f"Failed to extract text from {docx_file} even after image processing.")
                        return {"error": f"Text extraction failed for {docx_file}, even from images."}

                except Exception as e:
                    logging.error(f"Error processing images for {docx_file}: {str(e)}")
                    return {"error": f"Image processing failed for {docx_file}"}

            # Save the extracted information
            try:
                write_output_file(self.output_directory, docx_file, resume_info)
                logging.info(f"Processed DOCX file {docx_file} in {time.time() - start_time:.2f} seconds.")
                return {"message": f"Successfully processed {docx_file}"}
            except Exception as e:
                logging.error(f"Error writing output for {docx_file}: {str(e)}")
                return {"error": f"Failed to save extracted data for {docx_file}"}

        except Exception as e:
            logging.error(f"Unexpected error processing DOCX {docx_file}: {str(e)}")
            return {"error": f"Unexpected error while processing {docx_file}"}
        

    def process_doc_files(self, doc_file):
        """
        Processes .doc files by:
        1. Converting .doc → .docx.
        2. Extracting text from .docx.
        3. If text is empty, extracting from images.
        4. Calling extract_resume_info() only for renaming.
        5. Deleting the original .doc but keeping .docx.
        6. Writing output file.
        """
        start_time = time.time()
        doc_file_path = os.path.join(self.input_directory, doc_file)

        if not os.path.exists(doc_file_path):
            logging.error(f"File not found: {doc_file_path}. Skipping.")
            return {"error": f"File not found: {doc_file_path}"}

        try:
            # Step 1: Convert .doc to .docx
            docx_file_path = convert_doc_to_docx(doc_file_path)
            if not docx_file_path or not os.path.exists(docx_file_path):
                logging.error(f"Failed to convert {doc_file} to .docx. Skipping.")
                return {"error": f"Conversion failed for {doc_file}"}

            # Step 2: Delete the original .doc file after successful conversion
            try:
                os.remove(doc_file_path)
                logging.info(f"Deleted original DOC file: {doc_file_path}")
            except Exception as delete_error:
                logging.warning(f"Failed to delete DOC file {doc_file_path}: {delete_error}")

            extracted_text = ""  

            try:
                # Step 3: Extract text from .docx
                docx_loader = Docx2txtLoader(docx_file_path)
                extracted_text = "".join(page.page_content for page in docx_loader.load()).strip()

                # Step 4: If no text, extract from images
                if not extracted_text:
                    logging.warning(f"No text extracted from {doc_file}. Trying image extraction.")
                    combined_image_path = extract_and_combine_images_from_docx(docx_file_path)

                    if combined_image_path and os.path.exists(combined_image_path):
                        base64_image = self.encode_image_to_base64(combined_image_path)
                        extracted_text = self.client.call_gpt4o(base64_image)  # Directly save output

                        if not extracted_text:
                            logging.error(f"Failed to extract text from images in {doc_file}. Skipping.")
                            return {"error": f"Failed to extract text from images in {doc_file}"}

                        # Step 5: Write output directly for image-based extraction
                        write_output_file(self.output_directory, doc_file, extracted_text)

                        logging.info(f"Processed image-based DOC file {doc_file} in {time.time() - start_time:.2f} seconds.")
                        return {"success": f"Processed image-based DOC file {doc_file}"}

                # Step 6: Call extract_resume_info() **only for renaming** (text-based extraction)
                resume_info = self.client.extract_resume_info(extracted_text)
                write_output_file(self.output_directory, doc_file, resume_info)

                logging.info(f"Processed DOC file {doc_file} in {time.time() - start_time:.2f} seconds.")
                return {"success": f"Processed DOC file {doc_file}"}

            except Exception as e:
                logging.error(f"Error extracting text from DOCX {doc_file}: {str(e)}")
                return {"error": f"Error extracting text from {doc_file}: {str(e)}"}

        except Exception as e:
            logging.error(f"Critical error processing DOC {doc_file}: {str(e)}")
            return {"error": f"Critical error processing {doc_file}: {str(e)}"}

