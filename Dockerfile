FROM python:3.12-alpine

RUN apk add chromaprint ffmpeg
RUN mkdir /app
COPY pyproject.toml /app/pyproject.toml
COPY ./src/ider /app/ider
WORKDIR /app
RUN pip install -e .

CMD ["python", "ider/runner.py"]