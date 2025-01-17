# Use the official Python image from the Docker Hub
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file to the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install awscli and awscli-local
RUN pip install awscli awscli-local

# Copy the rest of the application code to the working directory
COPY . .

# Command to run the application
CMD ["python", "app.py"]
