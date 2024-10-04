import socket
import time
import os
import logging
import sys

# Set up logging to output to stdout
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# Define your service DNS name
nginx_service = "nginx.nginx.svc.cluster.local"

# Get the interval from environment variable, default to 10 seconds
interval = int(os.getenv("DNS_RESOLVE_INTERVAL_SECONDS", 10))

def resolve_dns(service_name):
    try:
        # Resolve DNS name to IP
        ip_address = socket.gethostbyname(service_name)
        logging.info(f"{service_name} resolved to {ip_address}")
    except socket.gaierror as e:
        logging.error(f"Failed to resolve {service_name}: {e}")

if __name__ == "__main__":
    while True:
        resolve_dns(nginx_service)
        # Sleep for the interval duration before next resolution
        time.sleep(interval)
