import requests
import json

# Simple test
test_data = {
    "content": "Machine learning and AI research",
    "max_urls": 3
}

try:
    response = requests.post("http://localhost:8000/fetch-web-urls", json=test_data, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
