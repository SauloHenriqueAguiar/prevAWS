# Use a slim Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application code and model into the container
# The model.xgb file will be added during the CI/CD process
COPY ./api/app.py /app/
COPY ./api/requirements-api.txt /app/

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements-api.txt

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application using uvicorn
# The model will be downloaded into /app/model.xgb by the CI/CD pipeline
ENV MODEL_PATH=/app/model.xgb
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]