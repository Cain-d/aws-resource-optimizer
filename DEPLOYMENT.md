# Deployment Guide

This guide covers all deployment options for AWS Resource Optimizer.

## Prerequisites

- AWS CLI installed and configured
- Appropriate AWS permissions (see [IAM Requirements](#iam-requirements))
- Python 3.8+ (for local development)

## Deployment Options

### 1. Quick Test (No AWS Deployment Required)

Perfect for trying out the tool without deploying infrastructure:

```bash
# Clone and setup
git clone https://github.com/cain-d/aws-resource-optimizer
cd aws-resource-optimizer
pip install -r requirements.txt

# Run against your AWS account
python src/main.py --profile default --regions us-east-1,us-west-2

# Generate HTML report
python src/main.py --profile default --output-format html --output-file report.html
```

### 2. Local Development with LocalStack

Test the full system locally without AWS costs:

```bash
# Setup LocalStack environment
./scripts/setup-local.sh

# This will:
# - Install LocalStack
# - Create mock AWS resources
# - Run the optimizer against mock data
# - Generate sample reports

# Run tests
python -m pytest tests/
```

### 3. AWS Cloud Deployment

#### Option A: CloudFormation (Recommended)

```bash
# Deploy the complete stack
aws cloudformation deploy \
  --template-file deployment/cloudformation/main.yaml \
  --stack-name aws-resource-optimizer \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    NotificationEmail=admin@company.com \
    ScanSchedule="rate(1 day)"

# Check deployment status
aws cloudformation describe-stacks --stack-name aws-resource-optimizer
```

#### Option B: CDK Deployment

```bash
cd deployment/cdk

# Install dependencies
npm install

# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy
cdk deploy --parameters notificationEmail=admin@company.com

# View outputs
cdk outputs
```

#### Option C: Terraform

```bash
cd deployment/terraform

# Initialize
terraform init

# Plan deployment
terraform plan -var="notification_email=admin@company.com"

# Deploy
terraform apply
```

## Configuration

### Environment Variables

```bash
# Required for AWS deployment
export AWS_REGION=us-east-1
export NOTIFICATION_EMAIL=admin@company.com

# Optional
export SCAN_SCHEDULE="rate(1 day)"  # How often to run scans
export LOG_LEVEL=INFO
export COST_THRESHOLD=100  # Only report resources costing more than $100/month
```

### Custom Thresholds

Edit `config/thresholds.yaml` before deployment:

```yaml
ec2:
  cpu_threshold: 5          # CPU utilization percentage
  network_threshold: 1000   # Network bytes per day
  days_to_analyze: 14       # Days of CloudWatch data to check

rds:
  cpu_threshold: 10
  connection_threshold: 5   # Database connections per day
  days_to_analyze: 7

ebs:
  iops_threshold: 10        # IOPS per day
  days_unattached: 7        # Days volume has been unattached
```

## IAM Requirements

### For Testing (Read-Only)

Attach these managed policies to your user/role:
- `ReadOnlyAccess`
- `CloudWatchReadOnlyAccess`

### For AWS Deployment

The CloudFormation template creates these roles automatically:
- Lambda execution role with resource scanning permissions
- EventBridge role for scheduling
- SNS role for notifications

### Custom IAM Policy (Minimal Permissions)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "rds:Describe*",
        "elasticloadbalancing:Describe*",
        "lambda:List*",
        "lambda:Get*",
        "cloudwatch:GetMetricStatistics",
        "cloudwatch:ListMetrics",
        "logs:DescribeLogGroups",
        "pricing:GetProducts"
      ],
      "Resource": "*"
    }
  ]
}
```

## Multi-Account Setup

For scanning multiple AWS accounts:

1. Deploy the stack in your central account
2. Create cross-account roles in target accounts
3. Update the configuration:

```yaml
accounts:
  - account_id: "123456789012"
    role_name: "ResourceOptimizerRole"
    regions: ["us-east-1", "us-west-2"]
  - account_id: "123456789013"
    role_name: "ResourceOptimizerRole"
    regions: ["eu-west-1"]
```

## Verification

After deployment, verify everything is working:

```bash
# Check Lambda function
aws lambda invoke --function-name resource-optimizer-scanner response.json
cat response.json

# Check S3 bucket for reports
aws s3 ls s3://resource-optimizer-reports-$(aws sts get-caller-identity --query Account --output text)

# Check CloudWatch logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/resource-optimizer"
```

## Troubleshooting

### Common Issues

**Permission Denied**
- Ensure your AWS credentials have the required permissions
- Check IAM roles are properly configured

**No Resources Found**
- Verify you're scanning the correct regions
- Check CloudWatch has sufficient data (may need 24-48 hours)

**High Costs**
- Adjust scan frequency in EventBridge rules
- Limit regions being scanned
- Increase thresholds to reduce noise

### Getting Help

- Check [GitHub Issues](https://github.com/cain-d/aws-resource-optimizer/issues)
- Review CloudWatch logs for detailed error messages
- Enable debug logging: `export LOG_LEVEL=DEBUG`

## Cost Estimation

Typical monthly costs for running in AWS:

- Lambda executions: $5-15
- CloudWatch metrics: $3-8  
- S3 storage: $1-3
- SNS notifications: $1-2
- **Total: $10-28/month**

Costs scale with:
- Number of resources in your account
- Scan frequency
- Number of regions scanned
- Report retention period