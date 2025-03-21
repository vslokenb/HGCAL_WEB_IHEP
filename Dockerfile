# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that Streamlit runs on
EXPOSE 8501

# Run Streamlit when the container launches
CMD ["streamlit", "run", "IHEP_MAC_Bookkeeping/website.py", "--server.port=8501", "--server.address=0.0.0.0"]
