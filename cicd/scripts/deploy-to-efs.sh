#!/bin/bash

# Deploy WordPress application to EFS
# This script is designed to run on EC2 instances with EFS mounted

set -e

# Configuration
ENVIRONMENT=${1:-"dev"}
STACK_NAME="wordpress-$ENVIRONMENT"
EFS_MOUNT_POINT="/var/www/html/wp-content"
BACKUP_DIR="/tmp/wp-content-backup-$(date +%Y%m%d-%H%M%S)"
DEPLOYMENT_DIR="/tmp/wordpress-deployment"

echo "🚀 Starting WordPress deployment to EFS..."
echo "Environment: $ENVIRONMENT"
echo "Stack: $STACK_NAME"
echo "EFS Mount Point: $EFS_MOUNT_POINT"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to handle errors
error_exit() {
    echo "❌ Error: $1" >&2
    exit 1
}

# Check if running on EC2 instance
if ! curl -s http://169.254.169.254/latest/meta-data/instance-id > /dev/null; then
    error_exit "This script must run on an EC2 instance"
fi

# Check if EFS is mounted
if ! mountpoint -q "$EFS_MOUNT_POINT"; then
    error_exit "EFS is not mounted at $EFS_MOUNT_POINT"
fi

# Get instance metadata
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
REGION=$(curl -s http://169.254.169.254/latest/meta-data/placement/region)

log "Instance ID: $INSTANCE_ID"
log "Region: $REGION"

# Download deployment package from S3 (assuming it was uploaded by CodeBuild)
log "Downloading deployment package..."

# Get the latest deployment artifact
BUCKET_NAME=$(aws cloudformation describe-stacks \
    --stack-name "wordpress-cicd" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`ArtifactsBucket`].OutputValue' \
    --output text 2>/dev/null || echo "")

if [ -z "$BUCKET_NAME" ]; then
    error_exit "Could not find artifacts bucket"
fi

log "Artifacts bucket: $BUCKET_NAME"

# Create deployment directory
mkdir -p "$DEPLOYMENT_DIR"
cd "$DEPLOYMENT_DIR"

# Download latest deployment package
aws s3 sync "s3://$BUCKET_NAME/wordpress-application/" . --region "$REGION" || error_exit "Failed to download deployment package"

# Create backup of current wp-content
if [ -d "$EFS_MOUNT_POINT" ] && [ "$(ls -A $EFS_MOUNT_POINT)" ]; then
    log "Creating backup of current wp-content..."
    mkdir -p "$BACKUP_DIR"
    cp -r "$EFS_MOUNT_POINT"/* "$BACKUP_DIR/" || log "Warning: Backup creation failed"
    log "Backup created at: $BACKUP_DIR"
fi

# Deploy themes
if [ -d "wp-content/themes" ]; then
    log "Deploying custom themes..."
    mkdir -p "$EFS_MOUNT_POINT/themes"
    
    for theme in wp-content/themes/*/; do
        if [ -d "$theme" ]; then
            theme_name=$(basename "$theme")
            log "Deploying theme: $theme_name"
            
            # Create theme backup
            if [ -d "$EFS_MOUNT_POINT/themes/$theme_name" ]; then
                cp -r "$EFS_MOUNT_POINT/themes/$theme_name" "$BACKUP_DIR/themes/$theme_name-backup" 2>/dev/null || true
            fi
            
            # Deploy theme
            cp -r "$theme" "$EFS_MOUNT_POINT/themes/" || error_exit "Failed to deploy theme: $theme_name"
        fi
    done
fi

# Deploy plugins
if [ -d "wp-content/plugins" ]; then
    log "Deploying custom plugins..."
    mkdir -p "$EFS_MOUNT_POINT/plugins"
    
    for plugin in wp-content/plugins/*/; do
        if [ -d "$plugin" ]; then
            plugin_name=$(basename "$plugin")
            log "Deploying plugin: $plugin_name"
            
            # Create plugin backup
            if [ -d "$EFS_MOUNT_POINT/plugins/$plugin_name" ]; then
                cp -r "$EFS_MOUNT_POINT/plugins/$plugin_name" "$BACKUP_DIR/plugins/$plugin_name-backup" 2>/dev/null || true
            fi
            
            # Deploy plugin
            cp -r "$plugin" "$EFS_MOUNT_POINT/plugins/" || error_exit "Failed to deploy plugin: $plugin_name"
        fi
    done
fi

# Deploy uploads and other content
if [ -d "wp-content/uploads" ]; then
    log "Deploying uploads..."
    mkdir -p "$EFS_MOUNT_POINT/uploads"
    cp -r wp-content/uploads/* "$EFS_MOUNT_POINT/uploads/" 2>/dev/null || true
fi

# Set proper permissions
log "Setting file permissions..."
chown -R apache:apache "$EFS_MOUNT_POINT" || log "Warning: Could not set ownership"
find "$EFS_MOUNT_POINT" -type d -exec chmod 755 {} \; || log "Warning: Could not set directory permissions"
find "$EFS_MOUNT_POINT" -type f -exec chmod 644 {} \; || log "Warning: Could not set file permissions"

# Create deployment log
DEPLOYMENT_LOG="$EFS_MOUNT_POINT/deployment-log.json"
cat > "$DEPLOYMENT_LOG" << EOF
{
    "deployment_time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "environment": "$ENVIRONMENT",
    "instance_id": "$INSTANCE_ID",
    "region": "$REGION",
    "backup_location": "$BACKUP_DIR",
    "status": "completed"
}
EOF

# Cleanup
rm -rf "$DEPLOYMENT_DIR"

log "✅ WordPress deployment completed successfully!"
log "Backup location: $BACKUP_DIR"
log "Deployment log: $DEPLOYMENT_LOG"

# Optional: Restart web services to pick up changes
if systemctl is-active --quiet httpd; then
    log "Restarting Apache..."
    systemctl restart httpd || log "Warning: Could not restart Apache"
fi

if systemctl is-active --quiet php-fpm; then
    log "Restarting PHP-FPM..."
    systemctl restart php-fpm || log "Warning: Could not restart PHP-FPM"
fi

log "🎉 Deployment completed successfully!"