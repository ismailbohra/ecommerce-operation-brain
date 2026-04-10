FROM python:3.11-slim

WORKDIR /app

COPY requirements-docker.txt .

RUN pip install -r requirements-docker.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
