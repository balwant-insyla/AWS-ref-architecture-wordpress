![](images/AWS_logo_PMS_300x180.png)

![](images/100x100_benefit_available.png)![](images/100x100_benefit_ingergration.png)![](images/100x100_benefit_ecryption-lock.png)![](images/100x100_benefit_fully-managed.png)![](images/100x100_benefit_lowcost-affordable.png)![](images/100x100_benefit_performance.png)![](images/100x100_benefit_scalable.png)![](images/100x100_benefit_storage.png)

# **Hosting WordPress on AWS - Updated**

### Version 3.0.0 (2024 Update)

---

This reference architecture provides **updated** CloudFormation templates for deploying WordPress on AWS with **current versions** and **security best practices**. The templates use modern AWS services including Aurora MySQL 8.0, PHP 8.3, WordPress 6.4+, and current generation EC2 instances.

## 🚀 What's New in Version 3.0.0

### **Updated Service Versions**
- **Aurora MySQL 8.0** (latest stable version)
- **PHP 8.3** (current stable release)
- **WordPress 6.4+** (latest versions supported)
- **Redis 7.0** for caching
- **Amazon Linux 2023** with dynamic AMI lookup

### **Current Generation Instances**
- **EC2**: t4g, m6i, r6g (Graviton-based for better price/performance)
- **RDS**: db.t4g, db.r6g instances
- **ElastiCache**: cache.t4g, cache.r7g instances

### **Enhanced Security**
- ✅ **HTTPS enforcement** with automatic HTTP→HTTPS redirect
- ✅ **EBS encryption** enabled by default
- ✅ **Database encryption** at rest and in transit
- ✅ **ElastiCache encryption** enabled
- ✅ **IMDSv2** enforced on EC2 instances
- ✅ **Restricted SSH access** (no 0.0.0.0/0 allowed)
- ✅ **Modern SSL policies** (TLS 1.2+)

### **Improved Monitoring**
- ✅ **CloudWatch agent** for centralized logging
- ✅ **Performance Insights** for RDS
- ✅ **Enhanced monitoring** with detailed metrics
- ✅ **Auto Scaling** based on CPU and memory metrics

## 📋 Prerequisites

- AWS CLI configured with appropriate permissions
- ACM certificate for HTTPS (recommended for production)
- EC2 Key Pair for SSH access
- Restricted CIDR block for SSH access (not 0.0.0.0/0)

## 🏗️ Architecture Overview

The updated architecture includes:

- **VPC** with public/private subnets across 3 AZs
- **Application Load Balancer** with HTTPS termination
- **Auto Scaling Group** with 2-6 EC2 instances
- **Aurora MySQL 8.0** cluster with read replica
- **ElastiCache Redis 7.0** for object caching
- **EFS** for shared WordPress files
- **CloudWatch** monitoring and alarms

## 🚀 Quick Start

### Option 1: Updated Templates (Recommended)

Use the updated templates with current versions:

```bash
# Clone the repository
git clone <your-repo-url>
cd aws-learning

# Deploy the updated stack
aws cloudformation create-stack \
  --stack-name wordpress-updated \
  --template-body file://templates/aws-refarch-wordpress-master-newvpc-updated.yaml \
  --parameters file://parameters-updated.json \
  --capabilities CAPABILITY_IAM
```

### Option 2: Original Templates (Legacy)

The original templates are still available for compatibility but are **not recommended** for new deployments due to outdated versions and security issues.

## 📝 Parameters

### Required Parameters
- **EC2KeyName**: EC2 Key Pair for SSH access
- **AdminEmail**: Email for WordPress admin and notifications
- **DatabaseMasterUsername**: Database username (8-16 chars)
- **DatabaseMasterPassword**: Database password (min 12 chars)

### Security Parameters
- **SshAccessCidr**: Restricted CIDR for SSH (default: 10.0.0.0/16)
- **PublicAlbAcmCertificate**: ACM certificate ARN for HTTPS
- **CloudFrontAcmCertificate**: ACM certificate for CloudFront (us-east-1)

### Instance Types (Current Generation)
- **WebInstanceType**: t4g.medium (default), m6i.large, etc.
- **DatabaseInstanceType**: db.t4g.medium (default), db.r6g.large, etc.
- **ElastiCacheNodeType**: cache.t4g.micro (default), cache.r7g.large, etc.

## 📁 Template Structure

### Updated Templates (Version 3.0.0)
```
templates/
├── aws-refarch-wordpress-master-newvpc-updated.yaml     # Master template
├── aws-refarch-wordpress-02-securitygroups-updated.yaml # Security groups
├── aws-refarch-wordpress-03-rds-updated.yaml            # Aurora MySQL 8.0
├── aws-refarch-wordpress-03-alb-updated.yaml            # Application Load Balancer
├── aws-refarch-wordpress-03-elasticache-updated.yaml    # Redis 7.0
├── aws-refarch-wordpress-04-web-updated.yaml            # Web tier (PHP 8.3)
└── aws-refarch-wordpress-01-newvpc-updated.yaml         # VPC (if needed)
```

### Legacy Templates (Version 2.0.2)
```
templates/
├── aws-refarch-wordpress-master-newvpc.yaml             # Original master
├── aws-refarch-wordpress-*.yaml                         # Original templates
```

## 🔧 Configuration

### PHP Configuration
The updated templates include optimized PHP 8.3 settings:
- Memory limit: 256M
- Upload max filesize: 64M
- OPcache enabled with optimized settings
- Error logging to CloudWatch

### WordPress Configuration
- Latest WordPress version support
- Redis object caching enabled
- W3 Total Cache plugin pre-installed
- SSL/HTTPS configuration
- Multi-site ready

### Database Configuration
- Aurora MySQL 8.0 with latest engine version
- Encryption at rest enabled
- Enhanced monitoring enabled
- Performance Insights enabled
- Automated backups (30 days retention)

## 📊 Monitoring & Alarms

### CloudWatch Alarms
- **Database**: CPU, connections, memory usage
- **Web Servers**: CPU, memory, disk usage
- **Load Balancer**: Response time, unhealthy hosts
- **Cache**: CPU, memory, evictions

### Logging
- Apache access/error logs → CloudWatch Logs
- PHP error logs → CloudWatch Logs
- System metrics → CloudWatch Metrics

## 🔒 Security Best Practices

### Network Security
- Private subnets for database and cache
- Security groups with least privilege
- No direct internet access to backend resources

### Data Protection
- EBS volumes encrypted
- RDS encryption at rest
- ElastiCache encryption in transit and at rest
- SSL/TLS for all communications

### Access Control
- IAM roles with minimal permissions
- Systems Manager for secure shell access
- Restricted SSH access via bastion host

## 💰 Cost Optimization

### Current Generation Instances
- **Graviton-based instances** (t4g, m6g, r6g) offer up to 40% better price/performance
- **gp3 EBS volumes** for better IOPS/cost ratio
- **Auto Scaling** to match capacity with demand

### Reserved Instances
Consider Reserved Instances for:
- RDS Aurora instances (1-3 year terms)
- ElastiCache nodes
- Predictable EC2 workloads

## 🚨 Migration from Version 2.0.2

### Breaking Changes
- PHP version updated from 5.6/7.0 to 8.2/8.3
- Aurora engine changed from `aurora` to `aurora-mysql`
- Instance types updated to current generation
- Security group rules tightened

### Migration Steps
1. **Backup** your existing WordPress site and database
2. **Test** the new templates in a staging environment
3. **Update** your parameter files for new instance types
4. **Deploy** new stack alongside existing (blue/green)
5. **Migrate** data and switch DNS

## 📞 Support

### Issues
- Check CloudWatch logs for application errors
- Review CloudFormation events for deployment issues
- Verify security group rules and network connectivity

### Best Practices
- Use ACM certificates for HTTPS
- Enable CloudTrail for audit logging
- Regular security updates via Systems Manager
- Monitor costs with AWS Cost Explorer

## 📄 License

This sample code is made available under the MIT-0 license. See the LICENSE file.

---

**⚠️ Important**: The original templates (version 2.0.2) contain outdated software versions and security vulnerabilities. Use the updated templates for new deployments.