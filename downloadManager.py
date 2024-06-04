import sys
import orjson
import logging
import requests
import gzip
import zipfile
import os
from progress.bar import ChargingBar
from io import BytesIO

# This script handles the downloading and extraction of JSON data from a given URL.
# It defines custom exception classes for handling errors during the process.
# The main function, download_and_extract, orchestrates the process by downloading the file,
# determining its type, and calling the appropriate extraction function.
# If errors occur during download or extraction, they are logged and re-raised to halt execution.
# The extraction functions decode JSON data from compressed files and return the filename and decoded JSON content.
# The script also includes a function, decode_json, to handle decoding JSON data with different encodings.
# It attempts native decoding first, then UTF-8, Latin-1, and UTF-16.


# Create a logger
logger = logging.getLogger(__name__)

# Configure logger to output log messages to stderr
handler = logging.StreamHandler(sys.stderr)
logger.addHandler(handler)

# Set log level
logger.setLevel(logging.INFO)


# Custom exception classes
class DownloadError(Exception):
    pass


class ExtractionError(Exception):
    pass


class TypeError(Exception):
    pass


# Function to download file from URL
def download_file(url, chunk_size=8200):
    try:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()

            content_type = response.headers.get('Content-Type', '')
            content_length = int(response.headers.get('Content-Length', 0))
            logger.info(f"File Type: {content_type}")
            logger.info(f"File Size: {content_length} bytes")

            with BytesIO() as file_buffer:
                # Initialize the progress bar
                bar = ChargingBar(f"Downloading File", max=content_length)
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        file_buffer.write(chunk)
                        # Update the progress bar
                        bar.next(len(chunk))
                # Finish the progress bar
                bar.finish()
                return file_buffer.getvalue(), content_type
    except requests.RequestException as e:
        raise DownloadError(f"Error downloading file from {url}: {e}")


def extract_json_from_zip(zip_data):
    try:
        with zipfile.ZipFile(BytesIO(zip_data)) as zip_file:
            # Check if there are non-JSON files in the archive
            other_files = [file for file in zip_file.namelist() if not file.endswith('.json')]
            if other_files:
                raise ExtractionError(f"Error: Found non-JSON file inside the ZIP archive: {other_files}")

            json_files = [file for file in zip_file.namelist() if file.endswith('.json')]
            if len(json_files) != 1:
                raise ExtractionError(f"Error: Expected exactly one JSON file inside the ZIP archive, found {len(json_files)} files")

            json_file_name = json_files[0]
            json_data = zip_file.read(json_file_name)
            json_decoded = decode_json(json_data)

            return json_file_name, json_decoded
    except (zipfile.BadZipFile, orjson.JSONDecodeError) as e:
        raise ExtractionError(f"Error extracting or decoding JSON from ZIP file: {e}")
    except ExtractionError as e:
        logger.error(e)
        raise


# Function to extract JSON data from GZIP file
def extract_json_from_gzip(gzip_data, gzip_file_name):
    try:
        with gzip.GzipFile(fileobj=BytesIO(gzip_data), mode='rb') as gzip_file:
            json_content = gzip_file.read()
            return os.path.splitext(gzip_file_name)[0], decode_json(json_content)
    except (gzip.BadGzipFile, orjson.JSONDecodeError) as e:
        raise ExtractionError(f"Error extracting JSON from GZIP file: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during GZIP file extraction: {e}")
        raise


# Function to decode JSON data with different encodings
def decode_json(data):
    encodings = ['utf-8', 'latin-1', 'utf-16', 'utf-16be', 'utf-32']

    for encoding in encodings:
        try:
            logger.info(f"Decoding data in {encoding}")
            return orjson.loads(data.decode(encoding))
        except UnicodeDecodeError:
            continue
        except orjson.JSONDecodeError as e:
            logger.error(f"Error decoding JSON data: {e}")
            return None

    logger.error("Unable to decode data")
    return None


# Function to download and extract JSON data from URL
def download_and_extract(url):
    try:
        file_data, content_type = download_file(url)
        if 'application/x-gzip' in content_type or file_data.startswith(b'\x1f\x8b\x08'):  # Gzip signature
            gzip_file_name = url.split("/")[-1]
            logger.info(f"Extracting GZip...")
            return extract_json_from_gzip(file_data, gzip_file_name)
        else:
            logger.info(f"Extracting Zip...")
            extracted_data = extract_json_from_zip(file_data)
            return extracted_data

    except TypeError as e:
        logger.error(f"Error while determining zip type: {e}")
        raise


# # Function to download file from URL ***trying to make it work with straight json files
# def download_file(url, chunk_size=8200):
#     try:
#         with requests.get(url, stream=True) as response:
#             response.raise_for_status()
#
#             content_type = response.headers.get('Content-Type', '')
#             content_length = int(response.headers.get('Content-Length', 0))
#             logger.info(f"File Type: {content_type}")
#             logger.info(f"File Size: {content_length} bytes")
#
#             # Initialize the progress bar
#             bar = ChargingBar(f"Downloading {url.split('/')[-1]}", max=content_length)
#
#             with BytesIO() as file_buffer:
#                 for chunk in response.iter_content(chunk_size=chunk_size):
#                     if chunk:
#                         file_buffer.write(chunk)
#                         # Update the progress bar
#                         bar.next(len(chunk))
#                 # Finish the progress bar
#                 bar.finish()
#                 return file_buffer.getvalue(), content_type
#     except requests.RequestException as e:
#         raise DownloadError(f"Error downloading file from {url}: {e}")
#
#
# # Function to extract JSON data
# def extract_json(file_data):
#     try:
#         json_data = file_data.decode('utf-8')
#         return 'data.json', orjson.loads(json_data)
#     except orjson.JSONDecodeError as e:
#         raise ExtractionError(f"Error decoding JSON data: {e}")
#
#
# # Function to extract JSON data from ZIP file
# def extract_json_from_zip(zip_data):
#     try:
#         with zipfile.ZipFile(BytesIO(zip_data)) as zip_file:
#             json_files = [file for file in zip_file.namelist() if file.endswith('.json')]
#             if len(json_files) != 1:
#                 raise ExtractionError(
#                     f"Expected exactly one JSON file inside the ZIP archive, found {len(json_files)} files")
#
#             # Check if there are non-JSON files in the archive
#             other_files = [file for file in zip_file.namelist() if not file.endswith('.json')]
#             if other_files:
#                 raise ExtractionError("Found non-JSON files inside the ZIP archive")
#
#             json_file_name = json_files[0]
#             json_data = zip_file.read(json_file_name)
#             return json_file_name, extract_json(json_data)
#     except (zipfile.BadZipFile, orjson.JSONDecodeError) as e:
#         raise ExtractionError(f"Error extracting or decoding JSON from ZIP file: {e}")
#
#
# # Function to extract JSON data from GZIP file
# def extract_json_from_gzip(gzip_data, gzip_file_name):
#     try:
#         with gzip.GzipFile(fileobj=BytesIO(gzip_data), mode='rb') as gzip_file:
#             json_content = gzip_file.read()
#             return os.path.splitext(gzip_file_name)[0], extract_json(json_content)
#     except (gzip.BadGzipFile, orjson.JSONDecodeError) as e:
#         raise ExtractionError(f"Error extracting JSON from GZIP file: {e}")
#
#
# # Function to download and extract JSON data from URL
# def download_and_extract(url):
#     try:
#         file_data, content_type = download_file(url)
#
#         # Check if the content type is JSON or if the file data starts with a JSON indicator
#         if 'application/json' in content_type or file_data.startswith(b'{'):
#             return extract_json(file_data)
#         elif file_data.startswith(b'\x1f\x8b\x08'):  # Gzip signature
#             gzip_file_name = url.split("/")[-1]
#             return extract_json_from_gzip(file_data, gzip_file_name)
#         else:
#             return extract_json_from_zip(file_data)
#     except (DownloadError, ExtractionError) as e:
#         logger.error(e)
#         raise  # Re-raise the exception to halt the execution
#     except Exception as e:
#         logger.error(f"Unexpected error: {e}")
#         raise