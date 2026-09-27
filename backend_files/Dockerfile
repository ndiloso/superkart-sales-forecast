# Python 3.13 matches the Colab runtime the model was trained in
FROM python:3.13-slim

# Working directory inside the container
WORKDIR /app

# Install dependencies first, so Docker can cache this layer between builds
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the API code and the serialized model
COPY . .

# The API listens on port 7860
EXPOSE 7860

# Serve the Flask app ("superkart_api" object in app.py) with gunicorn, 2 worker processes
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:7860", "app:superkart_api"]
