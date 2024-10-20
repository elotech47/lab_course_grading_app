# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application directory into the container
COPY . .

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Create a directory for the data if it doesn't exist
RUN mkdir -p /app/data

# Set environment variables if needed
ENV USE_GSHEETS=True
ENV SHEET_ID=1McjwAUswXeRIzh6SR1l2JPvG1hgeyt5RmH2H8YDZX98
ENV CREDENTIALS_PATH=me4611-grade-app-263030226390.json
ENV DATA_DIR=data
ENV ADMIN_SECRET_PHRASE=JustASecretPhrase-e10gh0s@

# Run the Streamlit app when the container launches
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]