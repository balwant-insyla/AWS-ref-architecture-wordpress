#!/bin/bash

# Setup GitHub integration for WordPress CI/CD pipeline

set -e

# Configuration
GITHUB_OWNER=""
GITHUB_REPO=""
GITHUB_TOKEN=""
AWS_REGION="us-east-1"
STACK_NAME="wordpress-cicd"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to prompt for input
prompt_input() {
    local prompt="$1"
    local var_name="$2"
    local is_secret="$3"
    
    if [ "$is_secret" = "true" ]; then
        read -s -p "$prompt: " input
        echo
    else
        read -p "$prompt: " input
    fi
    
    eval "$var_name='$input'"
}

print_status "🚀 Setting up GitHub integration for WordPress CI/CD pipeline"
echo

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    print_error "AWS CLI is not configured. Please run 'aws configure' first."
    exit 1
fi

print_status "✅ AWS CLI is configured"

# Get current AWS account and region
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region || echo "us-east-1")

print_status "AWS Account: $AWS_ACCOUNT"
print_status "AWS Region: $AWS_REGION"
echo

# Prompt for GitHub details if not provided
if [ -z "$GITHUB_OWNER" ]; then
    prompt_input "Enter your GitHub username/organization" GITHUB_OWNER
fi

if [ -z "$GITHUB_REPO" ]; then
    prompt_input "Enter your GitHub repository name" GITHUB_REPO
fi

if [ -z "$GITHUB_TOKEN" ]; then
    print_warning "You need a GitHub Personal Access Token with the following permissions:"
    echo "  - repo (Full control of private repositories)"
    echo "  - admin:repo_hook (Full control of repository hooks)"
    echo
    echo "Create one at: https://github.com/settings/tokens"
    echo
    prompt_input "Enter your GitHub Personal Access Token" GITHUB_TOKEN true
fi

echo
print_status "Configuration:"
print_status "  GitHub Owner: $GITHUB_OWNER"
print_status "  GitHub Repo: $GITHUB_REPO"
print_status "  AWS Account: $AWS_ACCOUNT"
print_status "  AWS Region: $AWS_REGION"
echo

# Validate GitHub repository access
print_status "🔍 Validating GitHub repository access..."

if curl -s -H "Authorization: token $GITHUB_TOKEN" \
   "https://api.github.com/repos/$GITHUB_OWNER/$GITHUB_REPO" > /dev/null; then
    print_status "✅ GitHub repository access validated"
else
    print_error "❌ Cannot access GitHub repository. Please check your token and repository details."
    exit 1
fi

# Check if repository has the required files
print_status "🔍 Checking repository structure..."

REPO_FILES=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    "https://api.github.com/repos/$GITHUB_OWNER/$GITHUB_REPO/contents")

if echo "$REPO_FILES" | grep -q "wordpress-complete-single-file.yaml"; then
    print_status "✅ WordPress template found in repository"
else
    print_warning "⚠️  WordPress template not found. Make sure to push your templates to the repository."
fi

# Deploy CI/CD infrastructure
print_status "🚀 Deploying CI/CD infrastructure..."

# Create parameters file
cat > /tmp/cicd-parameters.json << EOF
[
    {
        "ParameterKey": "GitHubOwner",
        "ParameterValue": "$GITHUB_OWNER"
    },
    {
        "ParameterKey": "GitHubRepo",
        "ParameterValue": "$GITHUB_REPO"
    },
    {
        "ParameterKey": "GitHubToken",
        "ParameterValue": "$GITHUB_TOKEN"
    },
    {
        "ParameterKey": "Environment",
        "ParameterValue": "dev"
    }
]
EOF

# Deploy the stack
if aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$AWS_REGION" > /dev/null 2>&1; then
    print_status "📝 Updating existing CI/CD stack..."
    aws cloudformation update-stack \
        --stack-name "$STACK_NAME" \
        --template-body file://templates/cicd-infrastructure.yaml \
        --parameters file:///tmp/cicd-parameters.json \
        --capabilities CAPABILITY_IAM \
        --region "$AWS_REGION"
else
    print_status "🆕 Creating new CI/CD stack..."
    aws cloudformation create-stack \
        --stack-name "$STACK_NAME" \
        --template-body file://templates/cicd-infrastructure.yaml \
        --parameters file:///tmp/cicd-parameters.json \
        --capabilities CAPABILITY_IAM \
        --region "$AWS_REGION"
fi

# Wait for stack to complete
print_status "⏳ Waiting for stack deployment to complete..."
aws cloudformation wait stack-create-complete --stack-name "$STACK_NAME" --region "$AWS_REGION" 2>/dev/null || \
aws cloudformation wait stack-update-complete --stack-name "$STACK_NAME" --region "$AWS_REGION" 2>/dev/null

if [ $? -eq 0 ]; then
    print_status "✅ CI/CD infrastructure deployed successfully!"
else
    print_error "❌ Stack deployment failed. Check the CloudFormation console for details."
    exit 1
fi

# Get stack outputs
print_status "📋 Getting stack outputs..."

ARTIFACTS_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$AWS_REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`ArtifactsBucket`].OutputValue' \
    --output text)

INFRASTRUCTURE_PIPELINE=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$AWS_REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`InfrastructurePipeline`].OutputValue' \
    --output text)

APPLICATION_PIPELINE=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$AWS_REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`ApplicationPipeline`].OutputValue' \
    --output text)

# Clean up temporary files
rm -f /tmp/cicd-parameters.json

echo
print_status "🎉 GitHub integration setup completed!"
echo
print_status "📋 Summary:"
print_status "  Artifacts Bucket: $ARTIFACTS_BUCKET"
print_status "  Infrastructure Pipeline: $INFRASTRUCTURE_PIPELINE"
print_status "  Application Pipeline: $APPLICATION_PIPELINE"
echo
print_status "🔗 Next Steps:"
print_status "  1. Push your WordPress templates to the GitHub repository"
print_status "  2. The infrastructure pipeline will automatically validate and deploy changes"
print_status "  3. The application pipeline will handle WordPress code deployments"
print_status "  4. Monitor pipelines in the AWS CodePipeline console"
echo
print_status "📖 Pipeline URLs:"
print_status "  Infrastructure: https://console.aws.amazon.com/codesuite/codepipeline/pipelines/$INFRASTRUCTURE_PIPELINE/view"
print_status "  Application: https://console.aws.amazon.com/codesuite/codepipeline/pipelines/$APPLICATION_PIPELINE/view"
echo
print_status "✨ Your WordPress CI/CD pipeline is ready!"