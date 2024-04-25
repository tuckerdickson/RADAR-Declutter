# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt .

# Install any dependencies needed for your application
RUN pip install --no-cache-dir -r requirements.txt

# Copy the contents of the src directory into the container at /app/src
COPY src/ /app/src/

# Expose the port your application runs on
EXPOSE 17000

# Define environment variables
ENV HOST="0.0.0.0"
ENV PORT="17000"

# Define the command to run your application
CMD ["python", "src/main.py", "listen", "--host", "$HOST", "--port", "$PORT"]
