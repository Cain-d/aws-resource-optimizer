#!/bin/bash

# AWS Resource Optimizer - Local Setup Script
# Sets up the project for local development with mock AWS services

set -e

echo "🚀 Setting up AWS Resource Optimizer for local development..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8+ and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    echo "Please install pip3 and try again."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p logs
mkdir -p reports
mkdir -p tests/fixtures

# Check if AWS CLI is installed (optional)
if command -v aws &> /dev/null; then
    echo "✅ AWS CLI found"
    
    # Check if AWS credentials are configured
    if aws sts get-caller-identity &> /dev/null; then
        echo "✅ AWS credentials are configured"
        echo "   You can run: python src/main.py --dry-run"
    else
        echo "⚠️  AWS credentials not configured"
        echo "   Configure with: aws configure"
        echo "   Or run in local mode: python src/main.py --local"
    fi
else
    echo "⚠️  AWS CLI not found (optional)"
    echo "   Install from: https://aws.amazon.com/cli/"
    echo "   Or run in local mode: python src/main.py --local"
fi

# Check if Docker is installed (for LocalStack)
if command -v docker &> /dev/null; then
    echo "✅ Docker found - you can use LocalStack for testing"
    echo "   Start LocalStack: docker run --rm -it -p 4566:4566 localstack/localstack"
else
    echo "⚠️  Docker not found (optional for LocalStack testing)"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Quick start options:"
echo "1. Test with your AWS account:    python src/main.py --dry-run"
echo "2. Run with mock data:           python src/main.py --local"
echo "3. Run tests:                    pytest tests/"
echo "4. View configuration:           cat config/thresholds.yaml"
echo ""
echo "For more options: python src/main.py --help"