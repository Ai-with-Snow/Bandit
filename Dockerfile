# Use the official Python 3.12 image as the base image
FROM python:3.12-slim

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Run proxy_server.py when the container launches
# Cloud Run expects the container to listen on $PORT
# proxy_server.py is configured to read PORT from env
CMD ["python", "proxy_server.py"]
