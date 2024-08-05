# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install MySQL client
RUN apt-get update && apt-get install -y default-mysql-client

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

#connecting to sqldb
ENV DB_HOST=host.docker.internal

# Copy the rest of the application code
COPY . .

# Command to run the application
CMD ["python", "run.py"]
