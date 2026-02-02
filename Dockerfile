# Base Image
FROM python:3.10-slim

# Setup
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

# Copy Code
COPY backend/ .

# Run
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]