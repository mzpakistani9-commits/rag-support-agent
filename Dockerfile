FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gradio --extra-index-url https://pypi.org/simple

COPY . .

ENV CHROMA_DIR=/tmp/chroma_db

EXPOSE 7860

CMD ["python", "demo/app.py"]