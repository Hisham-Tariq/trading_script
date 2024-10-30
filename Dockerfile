# Use the official lightweight Python image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose port 80 for the FastAPI app
EXPOSE 1521

# Run the FastAPI app with Uvicorn
CMD ["uvicorn", "web:app", "--host", "0.0.0.0", "--port", "1521"]