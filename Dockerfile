# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variable to mock mode for safety
ENV MOCK_MODE=True

# Command to run when the container starts
CMD ["python", "-m", "src.run_all"]
