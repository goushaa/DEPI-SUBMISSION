FROM python:3.9-slim

WORKDIR /app

COPY . /app

# Run the application
CMD ["python", "./dns_resolver.py"]
