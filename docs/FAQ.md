# Frequently Asked Questions

## General Questions

### What AWS services does this tool analyze?
Currently supports:
- EC2 instances (CPU utilization, stopped instances)
- RDS databases (connections, CPU utilization)
- EBS volumes (unattached volumes, low IOPS)

Additional services are planned for future releases.

### How accurate are the cost calculations?
Cost estimates are based on standard AWS pricing for common regions. Actual costs may vary based on:
- Reserved instances or savings plans
- Volume discounts
- Regional pricing differences
- Spot instance usage

For precise calculations, integrate with the AWS Cost Explorer API.

### Can I run this against multiple AWS accounts?
Yes, the tool supports multi-account scanning through cross-account IAM roles. See the deployment guide for configuration details.

## Technical Questions

### Why are some resources not showing up in scans?
Common reasons:
- Resources are too new (less than the configured analysis period)
- Resources have exclusion tags configured in your thresholds
- CloudWatch detailed monitoring is not enabled
- Insufficient IAM permissions

### How do I customize the detection thresholds?
Edit the `config/thresholds.yaml` file to adjust:
- CPU utilization percentages
- Analysis time periods
- Resource exclusion rules
- Cost thresholds

### Can I integrate this with my existing monitoring tools?
Yes, the tool outputs structured JSON that can be consumed by:
- Monitoring dashboards (Grafana, DataDog)
- Ticketing systems (JIRA, ServiceNow)
- Chat platforms (Slack, Teams)
- Custom automation workflows

## Deployment Questions

### What are the minimum IAM permissions required?
The tool requires read-only access to:
- EC2 (DescribeInstances, DescribeVolumes)
- RDS (DescribeDBInstances)
- CloudWatch (GetMetricStatistics)
- ELB (DescribeLoadBalancers)

See `deployment/iam-policy.json` for the complete policy.

### How much does it cost to run in AWS?
Typical monthly costs:
- Lambda execution: $5-15
- CloudWatch metrics: $3-8
- S3 storage: $1-3
- SNS notifications: $1-2

Total: $10-28/month depending on account size and scan frequency.

### Can I run this on-premises?
Yes, using LocalStack for development or by running the Python application directly against AWS APIs from your infrastructure.

## Troubleshooting

### "No credentials found" error
Ensure AWS credentials are configured:
```bash
aws configure
# or
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
```

### Lambda function timing out
For large AWS accounts, consider:
- Increasing Lambda timeout (max 15 minutes)
- Reducing the number of regions scanned
- Splitting scans across multiple Lambda invocations

### High number of false positives
Adjust thresholds in `config/thresholds.yaml`:
- Increase CPU utilization thresholds
- Extend analysis time periods
- Add exclusion tags for known resources

## Contributing

### How can I add support for new AWS services?
1. Create a new scanner class inheriting from `BaseScanner`
2. Implement the `scan()` method
3. Add configuration section to `thresholds.yaml`
4. Update the main application to include your scanner
5. Add tests and documentation

### How do I report bugs or request features?
- Open an issue on GitHub with detailed information
- Include log output and configuration details
- Provide steps to reproduce the issue

### Can I contribute cost optimization rules?
Yes! We welcome contributions for:
- New detection algorithms
- Cost calculation improvements
- Additional AWS service support
- Performance optimizations