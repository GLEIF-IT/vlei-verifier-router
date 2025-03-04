# Use Python 3.12 as the base image
FROM python:3.12-slim

WORKDIR /usr/local/var/server

COPY . .
RUN pip install --no-cache-dir -r requirements.txt


# Set the entrypoint
ENTRYPOINT ["python", "main.py"]
