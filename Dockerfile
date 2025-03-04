# Use the official Python image as the base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /movie-backend

# Copy requirements.txt first to leverage Docker caching
COPY requirements.txt /movie-backend/

# Install required dependencies
RUN pip install --no-cache-dir -r /movie-backend/requirements.txt

# Copy the application files
COPY src/ /movie-backend/src/
COPY app.py /movie-backend/

# Expose port 5000
EXPOSE 5000

# Define the command to run the application
CMD ["python", "app.py"]