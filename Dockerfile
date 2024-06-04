# Use an appropriate base image
FROM python:3.11

LABEL authors="jkunsman"

# Set the working directory
WORKDIR /app

# Install any dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY MRF-Validator-Tool .

ENV PYTHONUNBUFFERED=1
## Copy your validation script into the container
#COPY url_validator.py downloadManager.py /app/
#COPY schemas /app/
#COPY test /app/test
#COPY reports /app/reports

# Define the command to run your validation tool
ENTRYPOINT ["python", "url_validator.py"]