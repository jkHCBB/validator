import argparse
import logging
from concurrent.futures import ThreadPoolExecutor
import time
import orjson
from jsonschema import Draft7Validator
from pathlib import Path
import sys

# This script validates JSON data against a given schema.
# It loads JSON and schema files, performs validation using Draft7Validator from jsonschema library,
# and writes summarized error information to a report file in the 'reports' directory.
# If no errors are found, a message indicating the validity of the input JSON is appended to the report file.
# The script is intended for command-line use, accepting arguments for JSON file path (--file),
# schema file path (--schema), and an optional flag to disable the error limit (--no-limit).
# It measures execution time and logger.infos a completion message.
# Example usage:
# python local_file_validator.py --file jsonFiles/inn_file.json --schema schemas/inn_schema.json

# Create a logger
logger = logging.getLogger(__name__)

# Configure logger to output log messages to stderr
handler = logging.StreamHandler(sys.stderr)
logger.addHandler(handler)

# Set log level
logger.setLevel(logging.INFO)


def load_json_file(file_path):
    try:
        with open(file_path, 'rb') as json_file:
            return orjson.loads(json_file.read())
    except (orjson.JSONDecodeError, FileNotFoundError) as e:
        logger.info(f"Error loading JSON file: {e}")
        sys.exit(1)


def load_schema_file(schema_path):
    try:
        with open(schema_path, 'rb') as schema_file:
            return orjson.loads(schema_file.read())
    except FileNotFoundError as e:
        logger.info(f"Error loading schema file: {e}")
        sys.exit(1)


def validate_json(file, schema, output_directory, no_limit):
    try:

        instance = load_json_file(file)
        file_name = file.split("/")[-1]
        logger.info(file_name)
        # Create output filename based on the file_name
        output_filename = f"{file_name}_report.txt"
        output_path = output_directory / output_filename

        # Clear existing report file if it exists
        if output_path.exists():
            output_path.unlink()

        logger.info("Validation process started...")

        validator = Draft7Validator(schema)
        errors = list(validator.iter_errors(instance))

        error_counts = {}
        error_limit = 1000  # Hardcoded error limit
        error_counter = 0

        for error in errors:
            if error_counter >= error_limit:
                logger.info("*********WARNING: ERROR LIMIT REACHED!*********")
                break  # Break out of the loop if the error limit is reached

            error_message = error.message
            error_schema_path = list(error.relative_schema_path)[:-1]
            error_schema = error.schema

            key = (error_message, str(error_schema_path), str(error_schema))

            if key not in error_counts:
                error_counts[key] = {"count": 1}
            else:
                error_counts[key]["count"] += 1

            error_counter += 1  # Increment the error counter

        # Write summarized error information to the report file
        with open(output_path, 'a') as report_file:
            for (error_message, error_schema_path, error_schema), count in error_counts.items():
                report_file.write("-" * 30 + "\n")
                report_file.write(f"Error: {error_message}\n")
                report_file.write(f"Location: {error_schema_path}\n")
                report_file.write(f"Schema: {error_schema}\n")
                report_file.write(f"Count: {count}\n")
                report_file.write("-" * 30 + "\n")
                if no_limit:
                    continue
                if len(error_counts) >= 1000:
                    report_file.write("*********WARNING: ERROR LIMIT REACHED!*********\n")
                    break

        if not errors:
            logger.info("Input JSON is Valid")
            with open(output_path, 'a') as report_file:
                report_file.write("-" * 30 + "\n")
                report_file.write("Input JSON is Valid\n")
                report_file.write("-" * 30 + "\n")

    except Exception as e:
        logger.info(f"An unexpected error occurred: {e}")


def main():
    start_time = time.time()  # Start the timer

    parser = argparse.ArgumentParser(description='Validate JSON data against schema')
    parser.add_argument('--file', required=True, help='Path to the JSON file')
    parser.add_argument('--schema', required=True, help='Path to the JSON schema file')
    parser.add_argument('--no-limit', action='store_true', help='Disable error limit')  # Toggle to disable error limit
    args = parser.parse_args()

    # Load JSON schema
    with open(args.schema, 'rb') as json_file:  # Use binary mode for reading
        schema = orjson.loads(json_file.read())

    # reports directory
    reports_directory = "reports"
    output_directory = Path(__file__).parent / reports_directory

    # Create the reports directory if it doesn't exist
    output_directory.mkdir(parents=True, exist_ok=True)

    # Validate JSON data in parallel
    with ThreadPoolExecutor() as executor:
        executor.submit(validate_json, args.file, schema, output_directory, args.no_limit)

    end_time = time.time()  # Stop the timer
    duration = end_time - start_time
    logger.info(f"Entire program completed in {duration:.2f} seconds")
    logger.info("***Your Validation Report is Ready***")


if __name__ == "__main__":
    main()
