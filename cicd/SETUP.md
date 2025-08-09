# WordPress CI/CD Setup Guide

This guide will help you set up automated CI/CD pipelines for your WordPress infrastructure and application deployment.

## 🎯 Overview

The CI/CD setup provides:
- **Infrastructure Pipeline**: Automatically validates and deploys CloudFormation templates
- **Application Pipeline**: Handles WordPress code, themes, and plugins deployment
- **GitHub Integration**: Triggers on code changes
- **Multi-Environment Support**: Dev, Staging, Production

## 📋 Prerequisites

1. **AWS Account** with appropriate permissions
2. **GitHub Repository** with your WordPress code
3. **GitHub Personal Access Token** with repo permissions
4. **AWS CLI** configured locally

## 🚀 Quick Setup

### Step 1: Prepare GitHub Repository

1. Create a new GitHub repository or use existing one
2. Push your WordPress templates to the repository:
   ```bash
   git add templates/wordpress-complete-single-file.yaml
   git commit -m "Add WordPress CloudFormation template"
   git push origin main
   ```

### Step 2: Create GitHub Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token"
3. Select scopes:
   - `repo` (Full control of private repositories)
   - `admin:repo_hook` (Full control of repository hooks)
4. Copy the token (you'll need it in the next step)

### Step 3: Deploy CI/CD Infrastructure

Run the setup script:
```bash
cd cicd
./scripts/setup-github-integration.sh
```

The script will prompt you for:
- GitHub username/organization
- Repository name
- Personal access token
- AWS region (optional)

### Step 4: Verify Setup

1. Check CloudFormation console for the `wordpress-cicd` stack
2. Check CodePipeline console for your pipelines
3. Make a test commit to trigger the pipeline

## 📁 Repository Structure

Your GitHub repository should have this structure:
```
your-wordpress-repo/
├── templates/
│   └── wordpress-complete-single-file.yaml
├── wp-content/
│   ├── themes/
│   │   └── your-custom-theme/
│   └── plugins/
│       └── your-custom-plugin/
├── buildspec.yml (optional - for custom build steps)
└── README.md
```

## 🔄 How It Works

### Infrastructure Pipeline
1. **Trigger**: Push to `main` branch with template changes
2. **Validate**: Lint and validate CloudFormation templates
3. **Deploy**: Create/update WordPress infrastructure stack

### Application Pipeline
1. **Trigger**: Push to `main` branch with application changes
2. **Build**: Validate PHP syntax, check security
3. **Package**: Create deployment artifact
4. **Deploy**: Deploy to EFS via EC2 instances

## 🎛️ Pipeline Configuration

### Environment Variables
Set these in CodeBuild projects:
- `ENVIRONMENT`: Target environment (dev/staging/prod)
- `WORDPRESS_VERSION`: WordPress version to deploy
- `PHP_VERSION`: PHP version for validation

### Parameters Override
Update pipeline parameters in `cicd-infrastructure.yaml`:
```yaml
ParameterOverrides: |
  {
    "EC2KeyName": "your-key-pair",
    "AdminEmail": "admin@example.com",
    "DatabaseMasterUsername": "wpdbadmin",
    "DatabaseMasterPassword": "YourSecurePassword123!"
  }
```

## 🔧 Customization

### Custom Build Steps
Create `buildspec.yml` in your repository root:
```yaml
version: 0.2
phases:
  install:
    runtime-versions:
      php: 8.0
  build:
    commands:
      - echo "Custom build steps here"
```

### Multiple Environments
Deploy separate stacks for each environment:
```bash
# Deploy dev environment
aws cloudformation create-stack \
  --stack-name wordpress-cicd-dev \
  --template-body file://templates/cicd-infrastructure.yaml \
  --parameters ParameterKey=Environment,ParameterValue=dev

# Deploy prod environment  
aws cloudformation create-stack \
  --stack-name wordpress-cicd-prod \
  --template-body file://templates/cicd-infrastructure.yaml \
  --parameters ParameterKey=Environment,ParameterValue=prod
```

## 📊 Monitoring

### Pipeline Status
- **CodePipeline Console**: Monitor pipeline executions
- **CloudWatch Logs**: View build logs
- **SNS Notifications**: Get alerts on pipeline status

### Key Metrics
- Build success rate
- Deployment frequency
- Lead time for changes
- Mean time to recovery

## 🛠️ Troubleshooting

### Common Issues

**Pipeline fails at validation:**
- Check CloudFormation template syntax
- Verify IAM permissions
- Review cfn-lint output

**GitHub integration not working:**
- Verify personal access token permissions
- Check repository webhook configuration
- Ensure repository is accessible

**Deployment fails:**
- Check EC2 instance logs
- Verify EFS mount status
- Review file permissions

### Debug Commands
```bash
# Check pipeline status
aws codepipeline get-pipeline-state --name your-pipeline-name

# View build logs
aws logs describe-log-groups --log-group-name-prefix /aws/codebuild/

# Check CloudFormation events
aws cloudformation describe-stack-events --stack-name wordpress-dev
```

## 🔐 Security Best Practices

1. **Secrets Management**: Use AWS Secrets Manager for sensitive data
2. **IAM Roles**: Use least privilege principle
3. **Encryption**: Enable encryption for artifacts bucket
4. **Access Control**: Restrict GitHub webhook access
5. **Audit Logging**: Enable CloudTrail for API calls

## 📚 Additional Resources

- [AWS CodePipeline Documentation](https://docs.aws.amazon.com/codepipeline/)
- [AWS CodeBuild Documentation](https://docs.aws.amazon.com/codebuild/)
- [GitHub Webhooks](https://docs.github.com/en/developers/webhooks-and-events/webhooks)
- [WordPress CLI Documentation](https://wp-cli.org/)

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review AWS CloudFormation and CodePipeline logs
3. Verify GitHub repository structure and permissions
4. Test manual deployment first to isolate issues

---

**Happy Deploying! 🚀**