# AWS WordPress Production Architecture

![AWS Logo](images/AWS_logo_PMS_300x180.png)

A production-ready, secure, and scalable WordPress hosting solution on AWS using Infrastructure as Code (CloudFormation).

## 🏗️ Architecture Overview

This solution deploys a highly available WordPress architecture with:

- **Multi-AZ deployment** across 2 availability zones
- **Auto Scaling** web tier with Application Load Balancer
- **Aurora MySQL** cluster with read replicas
- **ElastiCache Redis** for performance optimization
- **EFS** for shared WordPress files
- **CloudFront CDN** for global content delivery
- **KMS encryption** for data at rest
- **CloudWatch monitoring** and alerting

![Architecture Diagram](images/aws-refarch-wordpress-v20171026.jpeg)

## 🚀 Quick Start

### Prerequisites

1. **AWS CLI** configured with appropriate permissions
2. **EC2 Key Pair** created in your target region
3. **Domain name** (optional) and **SSL certificate** in ACM
4. **Email address** for monitoring alerts

### Deploy the Stack

```bash
# Clone the repository
git clone <repository-url>
cd aws-learning

# Deploy the stack
aws cloudformation create-stack \
  --stack-name wordpress-prod \
  --template-body file://templates/aws-ref-arch-wp-prod-former2.yaml \
  --parameters \
    ParameterKey=KeyPairName,ParameterValue=my-key-pair \
    ParameterKey=NotificationEmail,ParameterValue=admin@example.com \
    ParameterKey=DBMasterPassword,ParameterValue=SecurePassword123 \
    ParameterKey=DomainName,ParameterValue=example.com \
    ParameterKey=SSLCertificateArn,ParameterValue=arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012 \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

### Monitor Deployment

```bash
# Check stack status
aws cloudformation describe-stacks --stack-name wordpress-prod --query 'Stacks[0].StackStatus'

# Get stack outputs
aws cloudformation describe-stacks --stack-name wordpress-prod --query 'Stacks[0].Outputs'
```

## 📋 Configuration Parameters

### Environment Configuration
| Parameter | Default | Description |
|-----------|---------|-------------|
| `Environment` | `prod` | Environment name (dev/staging/prod) |
| `ProjectName` | `wordpress` | Project name for resource naming |

### Network Configuration
| Parameter | Default | Description |
|-----------|---------|-------------|
| `VpcCidr` | `10.0.0.0/16` | CIDR block for VPC |
| `AvailabilityZones` | `us-east-1a,us-east-1b` | List of AZs (minimum 2) |

### Database Configuration
| Parameter | Default | Description |
|-----------|---------|-------------|
| `DBInstanceClass` | `db.t4g.medium` | RDS instance class |
| `DBMasterUsername` | `wpdbadmin` | Database master username |
| `DBMasterPassword` | *Required* | Database password (8-41 chars) |
| `DBName` | `wordpress` | WordPress database name |

### Web Tier Configuration
| Parameter | Default | Description |
|-----------|---------|-------------|
| `WebInstanceType` | `t3.medium` | EC2 instance type |
| `KeyPairName` | *Required* | EC2 Key Pair name |
| `MinSize` | `2` | Minimum web servers |
| `MaxSize` | `6` | Maximum web servers |
| `DesiredCapacity` | `2` | Desired web servers |

### Domain & SSL
| Parameter | Default | Description |
|-----------|---------|-------------|
| `DomainName` | `""` | Custom domain (optional) |
| `SSLCertificateArn` | `""` | ACM certificate ARN (optional) |
| `CreateCloudFront` | `true` | Create CloudFront distribution |

## 🔧 Post-Deployment Setup

### 1. Access WordPress

After deployment, get the load balancer DNS name:

```bash
aws cloudformation describe-stacks \
  --stack-name wordpress-prod \
  --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
  --output text
```

Navigate to the URL to complete WordPress installation.

### 2. Configure WordPress

1. **Database Connection**: Pre-configured automatically
2. **File Uploads**: Stored on EFS (shared across instances)
3. **Media Offloading**: Configure S3 plugin for media bucket
4. **Caching**: Install Redis Object Cache plugin

### 3. Enable Bastion Host (Optional)

```bash
# Scale up bastion host for SSH access
aws autoscaling update-auto-scaling-group \
  --auto-scaling-group-name wordpress-prod-bastion-asg \
  --desired-capacity 1
```

### 4. Configure Domain (If Using Custom Domain)

1. **Route 53**: Create hosted zone for your domain
2. **DNS Records**: Point domain to CloudFront or ALB
3. **SSL Certificate**: Ensure ACM certificate is validated

## 🛡️ Security Features

### Encryption
- **KMS encryption** for all data at rest
- **EFS encryption** for shared files
- **RDS encryption** for database
- **S3 encryption** for media and backups

### Network Security
- **Private subnets** for web and database tiers
- **Security groups** with least privilege access
- **NAT Gateways** for outbound internet access
- **No direct internet access** to database

### Access Control
- **IAM roles** with minimal required permissions
- **Bastion host** for secure SSH access
- **SSM Session Manager** support
- **S3 bucket policies** blocking public access

## 📊 Monitoring & Alerting

### CloudWatch Alarms
- High CPU utilization (web servers)
- High database CPU utilization
- Unhealthy ALB targets
- EFS burst credit balance

### Metrics Dashboard
Access CloudWatch dashboard for:
- Application performance metrics
- Database performance
- Network and security metrics
- Cost optimization insights

### SNS Notifications
Configure email alerts for:
- Infrastructure issues
- Performance degradation
- Security events

## 💰 Cost Optimization

### Instance Sizing
- **t3.medium** for web servers (adjust based on load)
- **db.t4g.medium** for database (scale as needed)
- **cache.t4g.micro** for Redis

### Storage Optimization
- **EFS Provisioned Throughput** (100 MiB/s)
- **S3 Lifecycle Policies** for backup retention
- **CloudFront** for reduced origin requests

### Auto Scaling
- **Minimum 2 instances** for high availability
- **Maximum 6 instances** for peak loads
- **Target tracking** based on CPU and requests

## 🔄 Backup & Recovery

### Automated Backups
- **RDS automated backups** (7-day retention)
- **EFS automatic backups** via AWS Backup
- **S3 versioning** for media files

### Disaster Recovery
- **Multi-AZ deployment** for high availability
- **Cross-region backup** replication (optional)
- **Point-in-time recovery** for database

## 🚀 Scaling Guidelines

### Vertical Scaling
```bash
# Update instance types
aws cloudformation update-stack \
  --stack-name wordpress-prod \
  --use-previous-template \
  --parameters ParameterKey=WebInstanceType,ParameterValue=t3.large
```

### Horizontal Scaling
```bash
# Increase capacity
aws autoscaling update-auto-scaling-group \
  --auto-scaling-group-name wordpress-prod-asg \
  --desired-capacity 4 \
  --max-size 10
```

## 🛠️ Maintenance

### Updates
- **WordPress core**: Update via admin dashboard
- **Plugins**: Regular security updates
- **OS patches**: Use SSM Patch Manager
- **Database**: Aurora auto-updates minor versions

### Performance Tuning
- **OPcache**: Pre-configured for PHP optimization
- **Redis**: Object and page caching
- **CloudFront**: CDN for static assets
- **EFS**: Provisioned throughput mode

## 🔍 Troubleshooting

### Common Issues

**WordPress Installation Issues**
```bash
# Check web server logs
aws logs filter-log-events \
  --log-group-name /aws/ec2/wordpress \
  --start-time $(date -d '1 hour ago' +%s)000
```

**Database Connection Issues**
```bash
# Test database connectivity from bastion
mysql -h <db-endpoint> -u wpdbadmin -p
```

**Performance Issues**
- Check CloudWatch metrics for CPU/memory usage
- Review EFS burst credit balance
- Monitor ALB target health

### Support Resources
- [AWS CloudFormation Documentation](https://docs.aws.amazon.com/cloudformation/)
- [WordPress on AWS Best Practices](https://aws.amazon.com/getting-started/hands-on/deploy-wordpress-with-amazon-rds/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

## 📝 License

This project is licensed under the MIT-0 License. See the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
- Create an issue in this repository
- Check AWS documentation
- Contact AWS Support for infrastructure issues

---

**⚠️ Important Notes:**
- This template creates billable AWS resources
- Review costs before deployment
- Use appropriate instance sizes for your workload
- Regularly update WordPress and plugins for security
- Monitor CloudWatch alarms and respond to alerts promptly