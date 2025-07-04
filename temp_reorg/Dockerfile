# Dockerfile for Robotics Knowledge Base
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip && \
    pip install -r scripts/requirements.txt
ENV PYTHONUNBUFFERED=1
CMD ["python", "scripts/verify_docs.py"]
