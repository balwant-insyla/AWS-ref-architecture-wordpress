#!/bin/bash
# Export current AWS resources to YAML

echo "# Current AWS Resources Configuration" > current-config.yaml
echo "# Generated on $(date)" >> current-config.yaml

# Export Kinesis streams
echo "kinesis:" >> current-config.yaml
aws kinesis list-streams --query 'StreamNames' --output yaml | sed 's/^/  /' >> current-config.yaml

# Export CloudWatch log groups
echo "cloudwatch_logs:" >> current-config.yaml
aws logs describe-log-groups --query 'logGroups[].logGroupName' --output yaml | sed 's/^/  /' >> current-config.yaml

# Export ES domains
echo "elasticsearch:" >> current-config.yaml
aws es list-domain-names --query 'DomainNames[].DomainName' --output yaml | sed 's/^/  /' >> current-config.yaml