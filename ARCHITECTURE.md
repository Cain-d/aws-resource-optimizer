# AWS Resource Optimizer - Architecture Overview

This document describes the system architecture, design decisions, and technical implementation of the AWS Resource Optimizer.

## System Architecture

### High-Level Architecture

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

### Component Overview

1. **Scanner Engine**: Core Python application that analyzes AWS resources
2. **AWS Services Integration**: Interfaces with EC2, RDS, EBS, CloudWatch APIs
3. **Configuration Management**: YAML-based configuration for thresholds and rules
4. **Reporting System**: Multiple output formats (JSON, HTML)
5. **Deployment Infrastructure**: CloudFormation, CDK, and Terraform templates
6. **Monitoring & Alerting**: CloudWatch dashboards and SNS notifications

## Technical Implementation

### Core Components

#### 1. Scanner Architecture

```python
BaseScanner (Abstract)
├── EC2Scanner
├── RDSScanner
├── EBSScanner
├── LambdaScanner (future)
└── ELBScanner (future)
```

**Design Principles:**
- **Extensible**: Plugin architecture for new AWS services
- **Configurable**: YAML-based threshold management
- **Resilient**: Handles API rate limits and transient failures
- **Efficient**: Multi-region parallel processing

#### 2. AWS Client Management

```python
AWSClientManager
├── Session Management
├── Multi-Region Support
├── Cross-Account Roles
├── LocalStack Integration
└── Credential Handling
```

**Features:**
- Automatic client caching and reuse
- Support for AWS profiles and IAM roles
- LocalStack integration for local development
- Graceful error handling for credential issues

#### 3. Configuration System

```yaml
# Hierarchical configuration structure
service_name:
  threshold_settings:
    cpu_threshold: 5
    days_to_check: 14
  exclusion_rules:
    exclude_tags: []
    exclude_types: []
```

**Benefits:**
- Environment-specific configurations
- Runtime threshold adjustments
- Tag-based resource exclusions
- Validation and default value handling

### Data Flow

1. **Initialization**
   - Load configuration from YAML
   - Initialize AWS clients with proper credentials
   - Set up logging and error handling

2. **Resource Discovery**
   - Query AWS APIs for resource inventory
   - Filter resources based on configuration rules
   - Handle pagination and rate limiting

3. **Metrics Analysis**
   - Retrieve CloudWatch metrics for each resource
   - Calculate utilization averages over time periods
   - Apply threshold-based analysis rules

4. **Cost Calculation**
   - Estimate monthly costs using AWS pricing data
   - Calculate potential savings for idle resources
   - Factor in regional pricing differences

5. **Report Generation**
   - Aggregate findings across all scanners
   - Generate structured output (JSON/HTML)
   - Include recommendations and metadata

6. **Notification & Storage**
   - Store reports in S3 with lifecycle policies
   - Send notifications via SNS (email/Slack)
   - Update CloudWatch dashboards

## Deployment Architecture

### Local Development

```
Developer Machine
├── Python Virtual Environment
├── LocalStack (Optional)
├── AWS CLI Configuration
└── Mock Data Generation
```

### AWS Cloud Deployment

```
AWS Account
├── Lambda Function (Scanner)
├── EventBridge Rule (Scheduler)
├── S3 Bucket (Reports)
├── SNS Topic (Notifications)
├── CloudWatch (Monitoring)
└── IAM Roles (Security)
```

### Multi-Account Setup

```
Central Account (Hub)
├── Lambda Function
├── Cross-Account Roles
└── Consolidated Reporting

Target Accounts (Spokes)
├── ResourceOptimizerRole
├── Read-Only Permissions
└── Regional Resources
```

## Security Design

### IAM Permissions

**Principle of Least Privilege:**
- Read-only access to AWS resources
- No modification or deletion permissions
- Scoped to specific resource types

**Cross-Account Access:**
- Assume role pattern for multi-account scanning
- Time-limited credentials
- Audit trail via CloudTrail

### Data Protection

**In Transit:**
- HTTPS for all API communications
- TLS encryption for data transfer

**At Rest:**
- S3 bucket encryption (AES-256)
- CloudWatch logs encryption
- No sensitive data in reports

**Access Control:**
- S3 bucket policies restrict access
- SNS topic permissions
- VPC endpoints for private communication

## Performance Considerations

### Scalability

**Horizontal Scaling:**
- Parallel region scanning
- Concurrent resource analysis
- Lambda auto-scaling

**Vertical Scaling:**
- Configurable Lambda memory/timeout
- Batch processing for large accounts
- Efficient API pagination

### Optimization Strategies

1. **Caching**: AWS client reuse and response caching
2. **Batching**: Group API calls where possible
3. **Filtering**: Early resource filtering to reduce processing
4. **Async Processing**: Non-blocking I/O operations

### Resource Limits

| Component | Limit | Mitigation |
|-----------|-------|------------|
| Lambda Timeout | 15 minutes | Split large accounts across multiple invocations |
| API Rate Limits | Service-specific | Exponential backoff and retry logic |
| Memory Usage | 3GB max | Stream processing for large datasets |

## Monitoring & Observability

### Metrics Collection

**Application Metrics:**
- Resources scanned per service
- Findings generated per scan
- Potential savings calculated
- Scan duration and performance

**Infrastructure Metrics:**
- Lambda execution metrics
- API call success/failure rates
- S3 storage utilization
- SNS delivery status

### Logging Strategy

**Structured Logging:**
```python
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "scanner": "EC2Scanner",
  "region": "us-east-1",
  "resources_found": 25,
  "findings": 3,
  "duration_ms": 1500
}
```

**Log Levels:**
- ERROR: Critical failures requiring attention
- WARN: Non-critical issues or configuration problems
- INFO: Normal operation and scan results
- DEBUG: Detailed execution information

### Alerting

**CloudWatch Alarms:**
- Lambda function errors
- Execution timeouts
- High cost findings
- Failed notifications

**SNS Integration:**
- Email notifications for scan results
- Slack webhooks for team alerts
- PagerDuty for critical issues

## CI/CD Pipeline

### Development Workflow

1. **Local Development**
   - Feature development with LocalStack
   - Unit testing with pytest
   - Code quality checks (black, flake8)

2. **Testing**
   - Unit tests with mocked AWS services
   - Integration tests with LocalStack
   - End-to-end testing in dev account

3. **Deployment**
   - Infrastructure as Code validation
   - Automated deployment via GitHub Actions
   - Blue/green deployment for Lambda updates

### Quality Gates

- **Code Coverage**: Minimum 80% test coverage
- **Security Scanning**: Static analysis with bandit
- **Dependency Scanning**: Vulnerability checks
- **Performance Testing**: Load testing with large accounts

## Future Enhancements

### Planned Features

1. **Additional Services**
   - Lambda functions analysis
   - ElastiCache clusters
   - Elasticsearch domains
   - NAT Gateways

2. **Advanced Analytics**
   - Machine learning for usage prediction
   - Trend analysis and forecasting
   - Anomaly detection

3. **Automation**
   - Automated resource cleanup (with approval)
   - Right-sizing recommendations
   - Reserved instance optimization

4. **Integration**
   - JIRA ticket creation
   - ServiceNow integration
   - Terraform plan generation
   - Cost allocation tags

### Extensibility Points

- **Plugin Architecture**: Custom scanner development
- **Webhook System**: External system integration
- **Custom Metrics**: User-defined analysis rules
- **Multi-Cloud**: Azure and GCP support

## Technical Decisions

### Why Python?

- **AWS SDK Maturity**: Well-established boto3 library with full service coverage
- **Community**: Extensive third-party libraries and examples
- **Readability**: Clear syntax reduces maintenance overhead
- **Libraries**: Strong ecosystem for data processing and analysis

### Why Serverless?

- **Cost Efficiency**: Pay only for execution time
- **Scalability**: Automatic scaling based on demand
- **Maintenance**: No server management required
- **Integration**: Native AWS service integration

### Why CloudFormation?

- **AWS Native**: First-class AWS support
- **Declarative**: Infrastructure as code
- **Rollback**: Automatic rollback on failures
- **Cross-Region**: Multi-region deployment support

## Contributing

### Development Setup

1. Clone repository and setup virtual environment
2. Install development dependencies
3. Configure pre-commit hooks
4. Run tests to verify setup

### Code Standards

- **PEP 8**: Python style guide compliance
- **Type Hints**: Use type annotations
- **Documentation**: Comprehensive docstrings
- **Testing**: Unit tests for all new features

### Architecture Guidelines

- **Single Responsibility**: Each class has one purpose
- **Open/Closed**: Open for extension, closed for modification
- **Dependency Injection**: Avoid tight coupling
- **Error Handling**: Graceful failure and recovery