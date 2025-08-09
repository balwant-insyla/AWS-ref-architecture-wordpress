# WordPress CI/CD Pipeline

This folder contains CI/CD automation for the WordPress infrastructure and application deployment.

## Structure

```
cicd/
├── templates/           # CloudFormation templates for CI/CD resources
├── buildspecs/         # CodeBuild build specifications
├── scripts/            # Deployment and utility scripts
└── README.md           # This file
```

## Components

### 1. Infrastructure Pipeline
- **Purpose**: Deploy/update CloudFormation stacks automatically
- **Trigger**: Changes to infrastructure templates
- **Flow**: GitHub → CodePipeline → CloudFormation → Deploy

### 2. Application Pipeline  
- **Purpose**: Deploy WordPress code, themes, plugins
- **Trigger**: Changes to WordPress application code
- **Flow**: GitHub → CodeBuild → Deploy to EC2/EFS

### 3. Content Pipeline
- **Purpose**: Deploy themes, plugins, configurations
- **Trigger**: Changes to wp-content
- **Flow**: GitHub → CodeBuild → Sync to EFS

## Setup Instructions

1. **Deploy CI/CD Infrastructure**:
   ```bash
   aws cloudformation create-stack \
     --stack-name wordpress-cicd \
     --template-body file://templates/cicd-infrastructure.yaml \
     --capabilities CAPABILITY_IAM
   ```

2. **Connect GitHub Repository**:
   - Create GitHub personal access token
   - Update CodePipeline source configuration

3. **Configure Build Projects**:
   - Infrastructure validation and deployment
   - Application testing and deployment

## Usage

### Manual Deployment (Current)
- Use AWS Console
- Upload templates manually
- Good for learning and one-off deployments

### CI/CD Deployment (Automated)
- Push code to GitHub
- Automatic testing and validation
- Automated deployment to environments
- Good for production and team collaboration

## Benefits

- **Consistency**: Same deployment process every time
- **Testing**: Automated validation before deployment
- **Speed**: Faster than manual console operations
- **Rollback**: Easy to revert to previous versions
- **Audit**: Complete deployment history

## Prerequisites

- GitHub repository with WordPress code
- AWS CLI configured
- Appropriate IAM permissions
- CodeCommit/GitHub integration setup