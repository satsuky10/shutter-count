FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends libimage-exiftool-perl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY shutter_count.py .

ENTRYPOINT ["python", "shutter_count.py"]
