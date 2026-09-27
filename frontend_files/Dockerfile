FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Streamlit's default port
EXPOSE 8501

# CORS/XSRF checks are disabled because Codespaces serves the app through a proxy;
# without this, file uploads (batch prediction) are rejected with a 403 error
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", \
     "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
