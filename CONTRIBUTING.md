# Contributing to AWS Resource Optimizer

Thank you for your interest in contributing to AWS Resource Optimizer! This document provides guidelines and information for contributors.

## How to Contribute

### Reporting Issues

Before creating an issue, please:
1. Check existing issues to avoid duplicates
2. Use the issue templates when available
3. Provide clear, detailed information including:
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, AWS region)
   - Relevant log output

### Suggesting Features

We welcome feature suggestions! Please:
1. Check if the feature already exists or is planned
2. Describe the use case and business value
3. Consider implementation complexity
4. Be open to discussion and iteration

### Code Contributions

#### Getting Started

1. **Fork the repository**
   ```bash
   git clone https://github.com/cain-d/aws-resource-optimizer
   cd aws-resource-optimizer
   ```

2. **Set up development environment**
   ```bash
   chmod +x scripts/setup-local.sh
   ./scripts/setup-local.sh
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/add-lambda-scanner
   ```

#### Development Guidelines

**Code Style:**
- Follow PEP 8 Python style guide
- Use meaningful variable and function names
- Add type hints for function parameters and return values
- Keep functions focused and single-purpose

**Documentation:**
- Add docstrings to all classes and functions
- Update README.md if adding new features
- Include inline comments for complex logic
- Update configuration documentation for new options

**Testing:**
- Write unit tests for new functionality
- Ensure existing tests pass
- Aim for >80% code coverage
- Test both success and error scenarios

**Example Code Structure:**
```python
def analyze_resource(resource: Dict[str, Any], config: Dict[str, Any]) -> List[Finding]:
    """
    Analyze a single AWS resource for optimization opportunities.
    
    Args:
        resource: AWS resource data from API
        config: Scanner configuration settings
        
    Returns:
        List of findings for the resource
        
    Raises:
        ValueError: If resource data is invalid
    """
    # Implementation here
    pass
```

#### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_main.py

# Run with verbose output
pytest -v tests/
```

#### Code Quality Checks

```bash
# Format code
black src/ tests/

# Check style
flake8 src/ tests/

# Type checking
mypy src/
```

### Adding New AWS Service Scanners

To add support for a new AWS service:

1. **Create scanner class**
   ```python
   # src/scanners/new_service_scanner.py
   from .base_scanner import BaseScanner
   
   class NewServiceScanner(BaseScanner):
       def scan(self) -> List[Dict[str, Any]]:
           # Implementation
           pass
   ```

2. **Add configuration section**
   ```yaml
   # config/thresholds.yaml
   new_service:
     threshold_setting: 10
     days_to_check: 14
   ```

3. **Update main.py**
   ```python
   from scanners.new_service_scanner import NewServiceScanner
   
   scanners = [
       # ... existing scanners
       NewServiceScanner(aws_client, config.get('new_service', {}))
   ]
   ```

4. **Add tests**
   ```python
   # tests/test_new_service_scanner.py
   def test_new_service_scanner():
       # Test implementation
       pass
   ```

### Pull Request Process

1. **Before submitting:**
   - Ensure all tests pass
   - Run code quality checks
   - Update documentation
   - Test locally with real AWS resources (if possible)

2. **Pull request description should include:**
   - Clear description of changes
   - Motivation and context
   - Testing performed
   - Screenshots (for UI changes)
   - Breaking changes (if any)

3. **Review process:**
   - Maintainers will review within 1-2 weeks
   - Address feedback promptly
   - Be open to suggestions and changes
   - Squash commits before merge

## Project Structure

```
aws-resource-optimizer/
├── src/
│   ├── main.py              # Application entry point
│   ├── scanners/            # Service-specific scanners
│   ├── reporters/           # Output format generators
│   └── utils/               # Shared utilities
├── tests/                   # Test files
├── config/                  # Configuration files
├── deployment/              # Infrastructure templates
├── scripts/                 # Utility scripts
└── docs/                    # Documentation
```

## Development Environment

### Prerequisites

- Python 3.8+
- AWS CLI configured
- Git
- (Optional) Docker for LocalStack testing

### Local Testing Options

1. **Mock Mode**: Test with generated mock data
   ```bash
   python src/main.py --local
   ```

2. **LocalStack**: Test with LocalStack AWS emulation
   ```bash
   docker run --rm -it -p 4566:4566 localstack/localstack
   python src/main.py --local
   ```

3. **Real AWS**: Test against your AWS account
   ```bash
   python src/main.py --profile default --dry-run
   ```

## Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to docs
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `question`: Further information is requested

## Roadmap

### Current Priorities
1. Additional AWS service support (Lambda, ELB, ElastiCache)
2. Machine learning-based usage prediction
3. Automated remediation capabilities
4. Multi-cloud support (Azure, GCP)

### Future Enhancements
- Web dashboard interface
- API endpoints for integration
- Custom plugin architecture
- Advanced cost modeling

## Getting Help

- **Documentation**: Check README.md and docs/
- **Issues**: Search existing GitHub issues
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact maintainers for sensitive issues

## Recognition

Contributors will be:
- Listed in the project README
- Mentioned in release notes
- Invited to join the maintainer team (for significant contributions)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make AWS Resource Optimizer better!