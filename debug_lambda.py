import json
import boto3
import os
import uuid
from datetime import datetime

def handler(event, context):
    # Debug: Log the incoming event
    print(f"Received event: {json.dumps(event)}")
    
    try:
        action = event.get('action', 'list')
        print(f"Action detected: {action}")
        
        if action == 'create':
            print("Calling create_test function")
            return create_test(event)
        elif action == 'list':
            print("Calling list_tests function")
            return list_tests()
        else:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Load Test Manager',
                    'actions': ['create', 'start', 'stop', 'status', 'results', 'list'],
                    'received_action': action
                })
            }
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def create_test(event):
    print("Inside create_test function")
    
    # Simple test without DynamoDB first
    test_id = str(uuid.uuid4())
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'testId': test_id,
            'message': 'Test configuration created successfully',
            'debug': 'create_test function executed'
        })
    }

def list_tests():
    print("Inside list_tests function")
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'tests': [],
            'debug': 'list_tests function executed'
        })
    }