# Use the official Python image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy the current directory contents
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the Streamlit app
CMD ["streamlit", "run", "dashboard/app.py"]