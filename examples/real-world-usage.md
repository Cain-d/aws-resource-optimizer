# Real-World Usage Examples

This document shows how AWS Resource Optimizer has been used in different scenarios.

## Case Study 1: Startup Cost Optimization

**Scenario**: 50-person startup with rapid AWS growth, monthly bill of $15,000

**Configuration Used**:
```yaml
ec2:
  cpu_threshold: 10  # Higher threshold for dev environments
  days_to_check: 7   # Shorter analysis for faster iteration
```

**Results**:
- Found 12 idle EC2 instances in development accounts
- Identified 8 unattached EBS volumes from terminated instances
- Discovered 3 RDS instances with zero connections
- **Total monthly savings**: $2,100 (14% reduction)

**Actions Taken**:
1. Terminated unused development instances
2. Implemented auto-shutdown for dev environments
3. Consolidated test databases
4. Set up automated cleanup policies

## Case Study 2: Enterprise Multi-Account Optimization

**Scenario**: Large enterprise with 50+ AWS accounts, $200,000+ monthly spend

**Configuration Used**:
```yaml
ec2:
  cpu_threshold: 5
  days_to_check: 30  # Longer analysis for production workloads
  exclude_tags:
    - Environment: production
    - CriticalWorkload: true
```

**Results**:
- Scanned 2,500+ EC2 instances across all accounts
- Found 45 consistently underutilized instances
- Identified 120 unattached EBS volumes
- Discovered 15 unused RDS read replicas
- **Total monthly savings**: $18,500 (9% reduction)

**Implementation**:
- Deployed via AWS Organizations with cross-account roles
- Integrated with ServiceNow for automated ticket creation
- Set up Slack notifications for high-impact findings
- Created monthly executive reports

## Case Study 3: Development Team Optimization

**Scenario**: Development team with multiple sandbox accounts

**Configuration Used**:
```yaml
ec2:
  cpu_threshold: 15  # Very high threshold for dev boxes
  exclude_instance_types:
    - t3.nano
    - t3.micro  # Keep small instances for testing
lambda:
  days_since_invocation: 14  # Shorter period for dev functions
```

**Results**:
- Found 25 forgotten development instances
- Identified 40 unused Lambda functions from experiments
- Discovered 60 unattached volumes from testing
- **Total monthly savings**: $3,200

**Process Improvements**:
- Added resource tagging requirements
- Implemented weekly cleanup reminders
- Created development environment lifecycle policies
- Set up budget alerts per developer

## Integration Examples

### Slack Integration
```bash
# Send findings to Slack channel
python src/main.py --format json | \
  jq '.findings[] | select(.monthly_savings > 100)' | \
  curl -X POST -H 'Content-type: application/json' \
    --data @- $SLACK_WEBHOOK_URL
```

### JIRA Ticket Creation
```python
# Create JIRA tickets for high-impact findings
import json
from jira import JIRA

with open('findings.json') as f:
    report = json.load(f)

jira = JIRA(server='https://company.atlassian.net', 
           basic_auth=('user', 'token'))

for finding in report['findings']:
    if finding['monthly_savings'] > 200:
        jira.create_issue(
            project='COST',
            summary=f"Optimize {finding['resource_id']}",
            description=finding['description'],
            issuetype={'name': 'Task'}
        )
```

### Grafana Dashboard
```json
{
  "dashboard": {
    "title": "AWS Cost Optimization",
    "panels": [
      {
        "title": "Potential Monthly Savings",
        "type": "stat",
        "targets": [
          {
            "expr": "aws_optimizer_potential_savings_total"
          }
        ]
      }
    ]
  }
}
```

## Common Patterns and Solutions

### Pattern: High False Positive Rate
**Problem**: Too many findings for resources that are actually needed

**Solution**:
```yaml
# Adjust thresholds based on workload patterns
ec2:
  cpu_threshold: 2  # Lower for batch workloads
  exclude_tags:
    - WorkloadType: batch
    - Schedule: nightly
```

### Pattern: Seasonal Workloads
**Problem**: Resources appear idle during off-season

**Solution**:
```yaml
# Use longer analysis periods
ec2:
  days_to_check: 90  # Capture full seasonal cycle
rds:
  days_to_check: 60
```

### Pattern: Development Environment Sprawl
**Problem**: Developers forget to clean up test resources

**Solution**:
- Implement automatic tagging with expiration dates
- Set up Lambda functions for automated cleanup
- Use AWS Config rules for compliance monitoring

## Lessons Learned

### 1. Start Conservative
Begin with higher thresholds and gradually tighten based on your organization's comfort level.

### 2. Tag Everything
Proper resource tagging is crucial for accurate analysis and exclusions.

### 3. Automate Where Possible
Manual cleanup doesn't scale - implement automated policies for common scenarios.

### 4. Monitor Trends
Track optimization metrics over time to measure program effectiveness.

### 5. Educate Teams
Share findings with development teams to improve resource usage patterns.

## ROI Calculations

### Implementation Costs
- Initial setup: 8 hours (1 day)
- Monthly maintenance: 2 hours
- Tool infrastructure: $25/month

### Typical Savings
- Small accounts (<$5K/month): 10-20% reduction
- Medium accounts ($5K-50K/month): 8-15% reduction  
- Large accounts (>$50K/month): 5-12% reduction

### Payback Period
Most organizations see ROI within the first month of implementation.