FROM python:3.12-bullseye

WORKDIR /app

RUN apt-get update \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "main.py"]
