import logging
from datetime import datetime
import requests
import json
from datetime import datetime
from gql.transport.requests import RequestsHTTPTransport
from gql import gql, Client

def log_crm_heartbeat():
    log_file = "/tmp/crm_heartbeat_log.txt"

    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive"

    with open(log_file, "a") as f:
        f.write(message + "\n")

    # Optional: verify GraphQL hello field
    try:
        query = {"query": "{ hello }"}
        response = requests.post("http://localhost:8000/graphql", json=query, timeout=5)
        if response.status_code == 200:
            with open(log_file, "a") as f:
                f.write(f"{timestamp} GraphQL hello response: {response.json()}\n")
        else:
            with open(log_file, "a") as f:
                f.write(f"{timestamp} GraphQL endpoint error: {response.status_code}\n")
    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{timestamp} GraphQL check failed: {e}\n")
