# Use a lightweight Python image
FROM python:3.10-slim

# 1. Install System Dependencies (Crucial for Graphviz!)
RUN apt-get update && apt-get install -y \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# 2. Set up app directory
WORKDIR /app

# 3. Copy files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# 4. Expose Streamlit port
EXPOSE 8080

# 5. Run the app
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]