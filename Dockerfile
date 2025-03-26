# Use an official Python image as a base
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the entire project directory into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure data directories exist and have the correct permissions
RUN mkdir -p /app/user /app/data
COPY user/ /app/user/
COPY data/ /app/data/

RUN chmod -R 777 /app/data
RUN chmod -R 777 /app/user
RUN chmod -R 777 /app/IHEP_MAC_Bookkeeping


# Expose the default Streamlit port
EXPOSE 8501

# Run Streamlit when the container starts
CMD ["streamlit", "run", "IHEP_MAC_Bookkeeping/website.py", "--server.port=8501", "--server.address=0.0.0.0"]
