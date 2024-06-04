# **JSON Data Validation Tool**

### **Overview:**

This tool is designed to validate JSON data files against predefined JSON schemas using the JSON Schema validation library. It provides a command-line interface (CLI) for easy usage when working with web based files and generates a detailed report highlighting any validation errors encountered.

### **Features:**

* Validate JSON data files against JSON schemas.
* Supports both in-network and out-of-network schema validation.
* Detailed error reporting with error type, message, schema path, and requirement.
* Ability to limit the number of reported errors.

### **Installation:**

* Clone this repository to your local machine

* Install the required dependencies using pip:

`pip install -r requirements.txt`

### **Usage:**

#### **For Local File Validation:**

* Download and place your JSON data files in the jsonFiles directory.
* Run the local file validation tool using the following command in the Terminal:
* `python local_file_validator.py --file  --schema `
* Example For an In-Network File:
`python local_file_validator.py --file jsonFiles/inn_file.json --schema schemas/inn_schema.json`


#### **For URL Validation:**

* Run the Url validation tool using the following command in the Terminal:

`python url_validator.py --schema  --url `

* Example For an Allowed_Amounts File:

` python url_validator.py --schema schemas/oon_schema.json --url https://mrf.healthcarebluebook.com/luminareHealth/298531`

* Check the generated report in the reports directory for validation results.

### **Error Limiting:**

* Currently, there is a 1000 error limit set in the validation tool. This means that if the tool encounters more than 1000 errors
* it will stop reporting errors and display a message indicating that the error limit has been reached. 
* This is intended to prevent the tool from getting stuck in an infinite loop when encountering a large number of errors.
* To change the error limit for the local_file_validator, modify the error_limit variable in the code. 
* Ex: error_limit = 1000  # Hardcoded error limit
* To change the error limit or disable it entirely for the url_validator, you can modify the error_limit variable in the code just as above or pass the argument '--no-limit' to the command line script. 
* Ex: `python url_validator.py --schema schemas/oon_schema.json --url https://mrf.healthcarebluebook.com/luminareHealth/298531 --no-limit` 

### **Updating**

* To update pip to the latest version, run the following command in the terminal:

`python.exe -m pip install --upgrade pip`

### **License:**

This project is licensed under the MIT License - see the LICENSE file for details.
