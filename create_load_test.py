#!/usr/bin/env python3
import requests
import json

def create_load_test():
    url = "https://zqqmooux6d.execute-api.us-east-1.amazonaws.com/prod/test"
    
    # Create a new load test
    payload = {
        "action": "create",
        "name": "WordPress API Load Test",
        "target_url": "https://your-wordpress-site.com",  # Replace with your WordPress URL
        "concurrent_users": 50,
        "duration": 300,  # 5 minutes
        "ramp_up": 60,    # 1 minute ramp up
        "regions": ["us-east-1", "us-west-2"]
    }
    
    response = requests.post(url, json=payload)
    print(f"Create Test Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        test_id = result.get('testId')
        print(f"\nTest ID: {test_id}")
        
        # Start the test
        start_payload = {
            "action": "start",
            "testId": test_id
        }
        
        start_response = requests.post(url, json=start_payload)
        print(f"\nStart Test Status: {start_response.status_code}")
        print(f"Start Response: {start_response.text}")

if __name__ == "__main__":
    create_load_test()