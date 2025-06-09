import requests
import json

ENDPOINT = "http://localhost:8000/products/createAll"  # Replace with your actual endpoint

def make_post_requests(payloads=None):
    try:


        response = requests.post(ENDPOINT, json=payloads, headers={'Content-Type': 'application/json'})
        print(f"Status: {response.status_code}, Response: {response.text}")
    except requests.RequestException as e:
        print(f"Request failed: {e}")


with open('/home/jose/Descargas/CardsScraper/data/prod_result_3.json', 'r') as file:
    data = json.load(file)
make_post_requests(data)