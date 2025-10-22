FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE $PORT

# Use shell form to ensure environment variables are expanded
CMD uvicorn main:app --host 0.0.0.0 --port $PORT --reload
