#!/usr/bin/env python3
import requests
import json
import time

def test_api_endpoint():
    url = "https://zqqmooux6d.execute-api.us-east-1.amazonaws.com/prod/test"
    
    print(f"Testing API endpoint: {url}")
    
    try:
        # GET request
        response = requests.get(url, timeout=10)
        print(f"GET Status: {response.status_code}")
        print(f"Response: {response.text}")
        print(f"Headers: {dict(response.headers)}")
        
        # POST request
        payload = {"test": "data", "timestamp": time.time()}
        response = requests.post(url, json=payload, timeout=10)
        print(f"\nPOST Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api_endpoint()