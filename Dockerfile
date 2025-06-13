FROM python:3.13-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    git \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*
COPY . /app/
WORKDIR  /app
ENV PYTHONPATH="/app:/app/src"
RUN pip install --upgrade pip setuptools wheel \ 
    && pip install --no-cache-dir -r requirements.txt
EXPOSE 8000 8501
CMD ["sh","-c","uvicorn src.app:app --host 0.0.0.0 --port 8000 & streamlit run main.py --server.port 8501 --server.address 0.0.0.0"]

