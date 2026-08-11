FROM python:3.13-bullseye

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install uv

CMD ["uv", "run", "main.py"]
