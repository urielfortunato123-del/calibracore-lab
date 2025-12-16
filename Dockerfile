# Use official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container to the project root
WORKDIR /app

# Copy the requirements file into the container
COPY backend/requirements.txt ./backend/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the rest of the application code
COPY . .

# Create the uploads directory inside the container
RUN mkdir -p uploads

# Expose the port the app runs on (Cloud Run uses 8080 by default, usually passed via $PORT)
ENV PORT=8080
EXPOSE 8080

# Change to backend directory to run the app
WORKDIR /app/backend

# Run the application
# We use shell form to expand $PORT
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
