# AWS Resource Optimizer

A production-ready tool for identifying idle AWS resources and calculating cost optimization opportunities across your cloud infrastructure.

## Features

- **Multi-Service Support**: Analyzes EC2, RDS, EBS, and more AWS services
- **Cost Calculation**: Estimates potential monthly savings for each finding
- **Flexible Deployment**: Run locally, deploy to AWS, or use with CI/CD
- **Configurable Rules**: Customize thresholds via YAML configuration
- **Multiple Output Formats**: JSON and HTML reports with detailed recommendations

## Quick Start

### Option 1: Test Against Your AWS Account (No Deployment)
```bash
git clone https://github.com/cain-d/aws-resource-optimizer
cd aws-resource-optimizer
pip install -r requirements.txt
python src/main.py --profile default --dry-run
```

### Option 2: Local Development with Mock Data
```bash
./scripts/setup-local.sh
python src/main.py --local
```

### Option 3: Deploy to AWS (Production)
```bash
# One-click deployment
aws cloudformation deploy --template-file deployment/cloudformation/main.yaml --stack-name resource-optimizer --capabilities CAPABILITY_IAM

# Or use CDK
cd deployment/cdk && npm install && cdk deploy
```

## What It Finds

- **EC2 Instances**: Low CPU utilization, stopped instances
- **RDS Databases**: Unused connections, oversized instances  
- **EBS Volumes**: Unattached volumes, low IOPS usage
- **Load Balancers**: No targets, low request count
- **Lambda Functions**: Never invoked, high error rates
- **CloudWatch Logs**: Retention policy optimization

## Cost Impact

Example findings from a typical AWS account:
- Idle EC2 instances: **$2,400/month savings**
- Unattached EBS volumes: **$180/month savings**
- Oversized RDS instances: **$800/month savings**
- **Total potential savings: $3,380/month**

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   EventBridge   │───▶│  Lambda Function │───▶│   S3 Reports    │
│   (Scheduler)   │    │   (Scanner)      │    │    Bucket       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   CloudWatch     │    │  SNS Topic      │
                       │   (Metrics)      │    │ (Notifications) │
                       └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │ Email/Slack     │
                                               │ Notifications   │
                                               └─────────────────┘
```

- **Serverless**: Runs on Lambda, pay only when scanning
- **Secure**: Least-privilege IAM roles, no data stored
- **Scalable**: Handles thousands of resources across multiple accounts
- **Configurable**: Customize thresholds and rules via YAML

## Requirements

- AWS CLI configured with appropriate permissions
- Python 3.8+ (for local development)
- Node.js 16+ (if using CDK deployment)

## Configuration

Customize detection rules in `config/thresholds.yaml`:

```yaml
ec2:
  cpu_threshold: 5  # Percent
  days_to_check: 14
  
rds:
  connection_threshold: 10  # Connections per day
  cpu_threshold: 10  # Percent
```

## Documentation

- [Deployment Guide](DEPLOYMENT.md) - Detailed setup instructions
- [Architecture Overview](ARCHITECTURE.md) - System design and decisions
- [FAQ](docs/FAQ.md) - Frequently asked questions
- [Real-World Usage](examples/real-world-usage.md) - Case studies and examples

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Estimated AWS costs to run**: $15-30/month for typical usage (see [DEPLOYMENT.md](DEPLOYMENT.md) for details)