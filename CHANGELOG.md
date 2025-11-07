# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of AWS Resource Optimizer
- EC2 instance utilization analysis
- RDS database connection monitoring
- EBS volume attachment tracking
- CloudFormation deployment template
- HTML and JSON report generation
- Multi-region scanning support
- Configurable threshold management

### Security
- IAM least-privilege access patterns
- No sensitive data in reports
- Encrypted S3 storage for reports

## [1.0.0] - 2024-01-15

### Added
- Core scanning engine for AWS resources
- Support for EC2, RDS, and EBS services
- Cost calculation and savings estimation
- Multiple deployment options (local, CloudFormation, CDK)
- Comprehensive documentation and examples
- CI/CD pipeline with automated testing
- LocalStack integration for local development