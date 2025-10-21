#!/bin/bash
echo "Starting Medical Coding API..."
echo "Current directory: C:\Users\DELL\Desktop\Medical Coding API"
echo "Python version: Python 3.13.7"
echo "PORT: "

pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port  --workers 1
