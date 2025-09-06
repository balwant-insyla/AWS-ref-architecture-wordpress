import json
import boto3
import os
import uuid
from datetime import datetime

def handler(event, context):
    try:
        # Handle API Gateway proxy integration
        if 'body' in event:
            # API Gateway request
            if event['body']:
                body = json.loads(event['body'])
            else:
                body = {}
        else:
            # Direct Lambda invocation
            body = event
        
        action = body.get('action', 'list')
        
        if action == 'create':
            return create_test(body)
        elif action == 'start':
            return start_test(body)
        elif action == 'stop':
            return stop_test(body)
        elif action == 'status':
            return get_test_status(body)
        elif action == 'results':
            return get_test_results(body)
        elif action == 'list':
            return list_tests()
        else:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Load Test Manager',
                    'actions': ['create', 'start', 'stop', 'status', 'results', 'list']
                })
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def create_test(event):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['CONFIG_TABLE'])
    
    test_id = str(uuid.uuid4())
    config = {
        'testId': test_id,
        'name': event.get('name', 'Load Test'),
        'target_url': event.get('target_url'),
        'concurrent_users': event.get('concurrent_users', 100),
        'duration': event.get('duration', 300),
        'ramp_up': event.get('ramp_up', 60),
        'regions': event.get('regions', os.environ['TEST_REGIONS'].split(',')),
        'created_at': datetime.utcnow().isoformat(),
        'status': 'created'
    }
    
    table.put_item(Item=config)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'testId': test_id,
            'message': 'Test configuration created successfully'
        })
    }

def start_test(event):
    test_id = event.get('testId')
    if not test_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'testId required'})
        }
    
    dynamodb = boto3.resource('dynamodb')
    config_table = dynamodb.Table(os.environ['CONFIG_TABLE'])
    
    config_table.update_item(
        Key={'testId': test_id},
        UpdateExpression='SET #status = :status, started_at = :started_at',
        ExpressionAttributeNames={'#status': 'status'},
        ExpressionAttributeValues={
            ':status': 'running',
            ':started_at': datetime.utcnow().isoformat()
        }
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Test started successfully'})
    }

def stop_test(event):
    test_id = event.get('testId')
    if not test_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'testId required'})
        }
    
    dynamodb = boto3.resource('dynamodb')
    config_table = dynamodb.Table(os.environ['CONFIG_TABLE'])
    
    config_table.update_item(
        Key={'testId': test_id},
        UpdateExpression='SET #status = :status, stopped_at = :stopped_at',
        ExpressionAttributeNames={'#status': 'status'},
        ExpressionAttributeValues={
            ':status': 'stopped',
            ':stopped_at': datetime.utcnow().isoformat()
        }
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Test stopped successfully'})
    }

def get_test_status(event):
    test_id = event.get('testId')
    if not test_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'testId required'})
        }
    
    dynamodb = boto3.resource('dynamodb')
    config_table = dynamodb.Table(os.environ['CONFIG_TABLE'])
    
    response = config_table.get_item(Key={'testId': test_id})
    if 'Item' not in response:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Test not found'})
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps(response['Item'], default=str)
    }

def get_test_results(event):
    test_id = event.get('testId')
    if not test_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'testId required'})
        }
    
    dynamodb = boto3.resource('dynamodb')
    results_table = dynamodb.Table(os.environ['RESULTS_TABLE'])
    
    response = results_table.query(
        KeyConditionExpression='testId = :testId',
        ExpressionAttributeValues={':testId': test_id}
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({'results': response.get('Items', [])}, default=str)
    }

def list_tests():
    dynamodb = boto3.resource('dynamodb')
    config_table = dynamodb.Table(os.environ['CONFIG_TABLE'])
    
    response = config_table.scan()
    
    return {
        'statusCode': 200,
        'body': json.dumps({'tests': response.get('Items', [])}, default=str)
    }