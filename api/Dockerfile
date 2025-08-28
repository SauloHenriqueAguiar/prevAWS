# Use a slim Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application code and model into the container
COPY app.py /app/
COPY requirements-api.txt /app/
COPY model.xgb /app/

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements-api.txt

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application using uvicorn
ENV MODEL_PATH=/app/model.xgb
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]