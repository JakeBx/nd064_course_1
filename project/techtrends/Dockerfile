# Use Python base image version 3.8
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Expose port 3111
EXPOSE 3111

# Copy the application files to the container
COPY . .

# Install packages defined in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run the init_db.py script to initialize the database
RUN python init_db.py

# Set the command to execute the application at container start
CMD ["python", "app.py"]