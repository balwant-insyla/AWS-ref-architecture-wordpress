#!/bin/bash
# Generate new CloudFormation template from existing resources

echo "AWSTemplateFormatVersion: '2010-09-09'" > new-template.yaml
echo "Description: 'Generated from existing production resources'" >> new-template.yaml
echo "Resources:" >> new-template.yaml

# Export Kinesis streams
for stream in $(aws kinesis list-streams --query 'StreamNames[]' --output text); do
  echo "  ${stream}Stream:" >> new-template.yaml
  echo "    Type: AWS::Kinesis::Stream" >> new-template.yaml
  echo "    Properties:" >> new-template.yaml
  aws kinesis describe-stream --stream-name $stream --query 'StreamDescription.{ShardCount:Shards[0].ShardId,RetentionPeriod:RetentionPeriodHours}' --output yaml | sed 's/^/      /' >> new-template.yaml
done