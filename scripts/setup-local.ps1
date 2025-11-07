# AWS Resource Optimizer - Local Setup Script (PowerShell)
# Sets up the project for local development with mock AWS services

Write-Host "Setting up AWS Resource Optimizer for local development..." -ForegroundColor Green

# Check if Python is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Python 3 is required but not installed." -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://python.org and try again." -ForegroundColor Yellow
    exit 1
}

# Check Python version
$pythonVersion = python --version 2>&1
Write-Host "Found $pythonVersion" -ForegroundColor Green

# Check if pip is installed
if (-not (Get-Command pip -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: pip is required but not installed." -ForegroundColor Red
    Write-Host "Please install pip and try again." -ForegroundColor Yellow
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& "venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

# Create necessary directories
Write-Host "Creating project directories..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
New-Item -ItemType Directory -Force -Path "reports" | Out-Null
New-Item -ItemType Directory -Force -Path "tests\fixtures" | Out-Null

# Check if AWS CLI is installed (optional)
if (Get-Command aws -ErrorAction SilentlyContinue) {
    Write-Host "AWS CLI found" -ForegroundColor Green
    
    # Check if AWS credentials are configured
    try {
        aws sts get-caller-identity | Out-Null
        Write-Host "AWS credentials are configured" -ForegroundColor Green
        Write-Host "   You can run: python src/main.py --dry-run" -ForegroundColor White
    }
    catch {
        Write-Host "WARNING: AWS credentials not configured" -ForegroundColor Yellow
        Write-Host "   Configure with: aws configure" -ForegroundColor White
        Write-Host "   Or run in local mode: python src/main.py --local" -ForegroundColor White
    }
}
else {
    Write-Host "WARNING: AWS CLI not found (optional)" -ForegroundColor Yellow
    Write-Host "   Install from: https://aws.amazon.com/cli/" -ForegroundColor White
    Write-Host "   Or run in local mode: python src/main.py --local" -ForegroundColor White
}

# Check if Docker is installed (for LocalStack)
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "Docker found - you can use LocalStack for testing" -ForegroundColor Green
    Write-Host "   Start LocalStack: docker run --rm -it -p 4566:4566 localstack/localstack" -ForegroundColor White
}
else {
    Write-Host "WARNING: Docker not found (optional for LocalStack testing)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Quick start options:" -ForegroundColor Cyan
Write-Host "1. Test with your AWS account:    python src/main.py --dry-run" -ForegroundColor White
Write-Host "2. Run with mock data:           python src/main.py --local" -ForegroundColor White
Write-Host "3. Run tests:                    pytest tests/" -ForegroundColor White
Write-Host "4. View configuration:           Get-Content config/thresholds.yaml" -ForegroundColor White
Write-Host ""
Write-Host "For more options: python src/main.py --help" -ForegroundColor White