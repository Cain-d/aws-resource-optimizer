#!/usr/bin/env python3
"""
AWS Resource Optimizer - Main Entry Point
Identifies idle AWS resources and calculates potential cost savings.
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from scanners.ec2_scanner import EC2Scanner
from scanners.rds_scanner import RDSScanner
from scanners.ebs_scanner import EBSScanner
from reporters.json_reporter import JSONReporter
from reporters.html_reporter import HTMLReporter
from utils.aws_client import AWSClientManager
from utils.config_loader import ConfigLoader


def setup_logging(level=logging.INFO):
    """Configure logging for the application."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('resource-optimizer.log')
        ]
    )


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description='AWS Resource Optimizer - Find idle resources and calculate savings'
    )
    parser.add_argument('--profile', help='AWS profile to use')
    parser.add_argument('--region', help='AWS region to scan (default: all regions)')
    parser.add_argument('--config', default='config/thresholds.yaml', 
                       help='Configuration file path')
    parser.add_argument('--output', default='findings.json', 
                       help='Output file path')
    parser.add_argument('--format', choices=['json', 'html'], default='json',
                       help='Output format')
    parser.add_argument('--dry-run', action='store_true',
                       help='Test run without making any changes')
    parser.add_argument('--local', action='store_true',
                       help='Run with mock data for local development')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting AWS Resource Optimizer")
    
    try:
        # Load configuration
        config = ConfigLoader.load(args.config)
        logger.info(f"Loaded configuration from {args.config}")
        
        # Initialize AWS client manager
        aws_client = AWSClientManager(
            profile=args.profile,
            region=args.region,
            local_mode=args.local
        )
        
        # Initialize scanners
        scanners = [
            EC2Scanner(aws_client, config.get('ec2', {})),
            RDSScanner(aws_client, config.get('rds', {})),
            EBSScanner(aws_client, config.get('ebs', {}))
        ]
        
        # Run scans
        all_findings = []
        total_potential_savings = 0
        
        for scanner in scanners:
            logger.info(f"Running {scanner.__class__.__name__}")
            findings = scanner.scan()
            all_findings.extend(findings)
            
            # Calculate savings for this scanner
            scanner_savings = sum(f.get('monthly_savings', 0) for f in findings)
            total_potential_savings += scanner_savings
            
            logger.info(f"{scanner.__class__.__name__} found {len(findings)} issues, "
                       f"potential savings: ${scanner_savings:.2f}/month")
        
        # Generate report
        report_data = {
            'scan_timestamp': datetime.utcnow().isoformat(),
            'total_findings': len(all_findings),
            'total_potential_savings': total_potential_savings,
            'findings': all_findings,
            'configuration': config
        }
        
        # Output results
        if args.format == 'json':
            reporter = JSONReporter()
        else:
            reporter = HTMLReporter()
        
        reporter.generate_report(report_data, args.output)
        
        logger.info(f"Scan complete! Found {len(all_findings)} issues with "
                   f"${total_potential_savings:.2f}/month potential savings")
        logger.info(f"Report saved to {args.output}")
        
        # Print summary to console
        print(f"\n🔍 AWS Resource Optimizer Results")
        print(f"{'='*50}")
        print(f"Total findings: {len(all_findings)}")
        print(f"Potential monthly savings: ${total_potential_savings:.2f}")
        print(f"Report saved to: {args.output}")
        
        if args.dry_run:
            print("\n⚠️  This was a dry run - no changes were made")
        
    except Exception as e:
        logger.error(f"Error during execution: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()