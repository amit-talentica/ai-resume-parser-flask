import time
import os
import logging

import os
import time
import logging
import json  # Make sure to import json

def read_file(file_path):
    """Read file content and return it."""
    with open(file_path, 'r') as file:
        return file.read()

def write_output_file(output_directory, filename, extracted_text, write_all=False, write_new=False):
    """Writes extracted text to a JSON file, handling --write-all and --write-new flags."""
    start_time = time.time()
    
    # Construct output file path
    output_filename = os.path.splitext(filename)[0] + "_extracted_info.json"
    output_filepath = os.path.join(output_directory, output_filename)

    # Check if file exists
    file_exists = os.path.exists(output_filepath)

    # Handle --write-all and --write-new flags
    if file_exists and not write_all:
        if write_new:
            logging.info(f"Skipping existing file: {output_filepath}")
            return None  # Skip processing if file already exists and --write-new is set
        else:
            logging.info(f"File already exists: {output_filepath}")
            return output_filepath  # Return existing file path

    # Write extracted text to JSON file
    try:
        with open(output_filepath, "w", encoding="utf-8") as json_file:
            #json.dump(extracted_text, json_file, ensure_ascii=False, indent=4)  # Assuming extracted_text is a dictionary or list
            json_file.write(extracted_text)
            json_file.write("\n")
            logging.info(f"Successfully written to: {output_filepath}")
    except Exception as e:
        logging.error(f"Failed to write file {output_filepath}: {e}")
        return None

    end_time = time.time()
    logging.info(f"Time taken to write file: {end_time - start_time:.2f} seconds")

    return output_filepath

