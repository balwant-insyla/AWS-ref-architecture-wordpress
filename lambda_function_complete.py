import json
import boto3
import os
import uuid
from datetime import datetime

def handler(event, context):
    try:
        # Handle API Gateway proxy integration
        if 'body' in event:
            if event['body']:
                body = json.loads(event['body'])
            else:
                body = {}
        else:
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
    regions = event.get('regions', os.environ.get('TEST_REGIONS', 'us-east-1').split(','))
    
    config = {
        'testId': test_id,
        'name': event.get('name', 'Load Test'),
        'target_url': event.get('target_url'),
        'concurrent_users': int(event.get('concurrent_users', 10)),
        'duration': int(event.get('duration', 60)),
        'ramp_up': int(event.get('ramp_up', 10)),
        'regions': regions,
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
    
    response = config_table.get_item(Key={'testId': test_id})
    if 'Item' not in response:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Test not found'})
        }
    
    config = response['Item']
    ec2 = boto3.client('ec2')
    
    user_data = f'''#!/bin/bash
export AWS_DEFAULT_REGION=us-east-1
yum update -y
yum install -y httpd-tools python3 pip
pip3 install boto3

# Run load test with realistic browser headers to bypass bot protection
ab -c {config['concurrent_users']} -t {config['duration']} -k -r -l \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" \
  -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8" \
  -H "Accept-Language: en-US,en;q=0.5" \
  -H "Accept-Encoding: gzip, deflate, br" \
  -H "DNT: 1" \
  -H "Connection: keep-alive" \
  -H "Upgrade-Insecure-Requests: 1" \
  "{config['target_url']}" > /tmp/results.txt 2>&1

# Upload results to DynamoDB
python3 << 'EOF'
import boto3
import os
from datetime import datetime

os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

try:
    with open('/tmp/results.txt', 'r') as f:
        results = f.read()
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('{os.environ["RESULTS_TABLE"]}')
    
    table.put_item(Item={{
        'testId': '{test_id}',
        'timestamp': datetime.utcnow().isoformat(),
        'results': results,
        'region': 'us-east-1'
    }})
    print("Results uploaded successfully")
except Exception as e:
    print(f"Error uploading results: {{e}}")
EOF

# Self-terminate the instance
python3 << 'TERMINATE'
import boto3
import requests
import time

try:
    # Wait a moment for results upload to complete
    time.sleep(5)
    
    # Get instance ID from metadata
    instance_id = requests.get('http://169.254.169.254/latest/meta-data/instance-id', timeout=10).text
    
    # Terminate the instance
    ec2 = boto3.client('ec2', region_name='us-east-1')
    ec2.terminate_instances(InstanceIds=[instance_id])
    print(f"Instance {{instance_id}} terminated successfully")
except Exception as e:
    print(f"Error terminating instance: {{e}}")
    # Fallback to shutdown if termination fails
    import os
    os.system('shutdown -h +1')
TERMINATE
'''
    
    try:
        response = ec2.run_instances(
            ImageId='ami-0c02fb55956c7d316',
            MinCount=1,
            MaxCount=1,
            InstanceType='t3.micro',
            IamInstanceProfile={'Arn': os.environ['INSTANCE_PROFILE']},
            SubnetId=os.environ['SUBNET_ID'],
            SecurityGroupIds=[os.environ['SECURITY_GROUP_ID']],
            UserData=user_data,
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [
                    {'Key': 'Name', 'Value': f'LoadTest-{test_id[:8]}'},
                    {'Key': 'TestId', 'Value': test_id}
                ]
            }]
        )
        
        config_table.update_item(
            Key={'testId': test_id},
            UpdateExpression='SET #status = :status, started_at = :started_at, instance_id = :instance_id',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'running',
                ':started_at': datetime.utcnow().isoformat(),
                ':instance_id': response['Instances'][0]['InstanceId']
            }
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Test started successfully, EC2 instance launched',
                'instance_id': response['Instances'][0]['InstanceId']
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Failed to launch instance: {str(e)}'})
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
    
    try:
        response = results_table.query(
            KeyConditionExpression='testId = :testId',
            ExpressionAttributeValues={':testId': test_id}
        )
    except Exception:
        response = {'Items': []}
    
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