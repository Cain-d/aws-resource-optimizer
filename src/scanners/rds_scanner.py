"""
RDS Scanner - Identifies idle and underutilized RDS instances.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any

from .base_scanner import BaseScanner


class RDSScanner(BaseScanner):
    """Scanner for RDS instances to identify idle and underutilized databases."""
    
    def scan(self) -> List[Dict[str, Any]]:
        """
        Scan RDS instances for idle and underutilized resources.
        
        Returns:
            List of findings
        """
        findings = []
        
        try:
            # Get all regions if not specified
            regions = self.aws_client.get_regions('rds') if not self.aws_client.region else [self.aws_client.region]
            
            for region in regions:
                self.logger.info(f"Scanning RDS instances in region: {region}")
                regional_rds = self.aws_client.get_client('rds', region)
                
                # Get all RDS instances
                paginator = regional_rds.get_paginator('describe_db_instances')
                
                for page in paginator.paginate():
                    for db_instance in page['DBInstances']:
                        instance_findings = self._analyze_db_instance(db_instance, region)
                        findings.extend(instance_findings)
                        
        except Exception as e:
            self.logger.error(f"Error scanning RDS instances: {str(e)}")
            
        return findings
    
    def _analyze_db_instance(self, db_instance: Dict[str, Any], region: str) -> List[Dict[str, Any]]:
        """
        Analyze a single RDS instance for issues.
        
        Args:
            db_instance: RDS instance data
            region: AWS region
            
        Returns:
            List of findings for this instance
        """
        findings = []
        db_identifier = db_instance['DBInstanceIdentifier']
        db_class = db_instance['DBInstanceClass']
        db_status = db_instance['DBInstanceStatus']
        
        # Skip instances that are not available
        if db_status != 'available':
            return findings
        
        # Check if instance should be excluded based on engine
        engine = db_instance.get('Engine', '')
        exclude_engines = self.config.get('exclude_engines', [])
        if engine in exclude_engines:
            return findings
        
        # Check instance age
        creation_time = db_instance.get('InstanceCreateTime')
        if creation_time:
            age_days = (datetime.utcnow() - creation_time.replace(tzinfo=None)).days
            min_age = self.config.get('minimum_age_days', 7)
            if age_days < min_age:
                self.logger.debug(f"Skipping {db_identifier} - too new ({age_days} days)")
                return findings
        
        # Check CPU utilization
        cpu_findings = self._check_cpu_utilization(db_instance, region)
        findings.extend(cpu_findings)
        
        # Check database connections
        connection_findings = self._check_database_connections(db_instance, region)
        findings.extend(connection_findings)
        
        return findings
    
    def _check_cpu_utilization(self, db_instance: Dict[str, Any], region: str) -> List[Dict[str, Any]]:
        """Check CPU utilization for RDS instance."""
        findings = []
        db_identifier = db_instance['DBInstanceIdentifier']
        db_class = db_instance['DBInstanceClass']
        
        # Get CPU utilization metrics
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=self.config.get('days_to_check', 14))
        
        dimensions = [
            {'Name': 'DBInstanceIdentifier', 'Value': db_identifier}
        ]
        
        cpu_values = self.get_cloudwatch_metrics(
            namespace='AWS/RDS',
            metric_name='CPUUtilization',
            dimensions=dimensions,
            start_time=start_time,
            end_time=end_time
        )
        
        if cpu_values:
            avg_cpu = sum(cpu_values) / len(cpu_values)
            cpu_threshold = self.config.get('cpu_threshold', 10)
            
            if avg_cpu < cpu_threshold:
                monthly_savings = self.calculate_cost_savings('rds', db_class, region)
                
                severity = 'high' if avg_cpu < 2 else 'medium'
                
                findings.append(self.create_finding(
                    resource_id=db_identifier,
                    resource_type='RDS',
                    issue_type='low_cpu_utilization',
                    description=f"RDS instance {db_identifier} has low CPU utilization: {avg_cpu:.1f}% average",
                    monthly_savings=monthly_savings,
                    recommendation="Consider downsizing to smaller instance class or review if database is needed",
                    severity=severity,
                    metadata={
                        'db_class': db_class,
                        'engine': db_instance.get('Engine', ''),
                        'region': region,
                        'avg_cpu_utilization': round(avg_cpu, 2),
                        'days_analyzed': self.config.get('days_to_check', 14)
                    }
                ))
        
        return findings
    
    def _check_database_connections(self, db_instance: Dict[str, Any], region: str) -> List[Dict[str, Any]]:
        """Check database connection count."""
        findings = []
        db_identifier = db_instance['DBInstanceIdentifier']
        db_class = db_instance['DBInstanceClass']
        
        # Get database connection metrics
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=self.config.get('days_to_check', 14))
        
        dimensions = [
            {'Name': 'DBInstanceIdentifier', 'Value': db_identifier}
        ]
        
        connection_values = self.get_cloudwatch_metrics(
            namespace='AWS/RDS',
            metric_name='DatabaseConnections',
            dimensions=dimensions,
            start_time=start_time,
            end_time=end_time
        )
        
        if connection_values:
            avg_connections = sum(connection_values) / len(connection_values)
            connection_threshold = self.config.get('connection_threshold', 5)
            
            if avg_connections < connection_threshold:
                monthly_savings = self.calculate_cost_savings('rds', db_class, region)
                
                severity = 'high' if avg_connections < 1 else 'medium'
                
                findings.append(self.create_finding(
                    resource_id=db_identifier,
                    resource_type='RDS',
                    issue_type='low_connection_count',
                    description=f"RDS instance {db_identifier} has low connection count: {avg_connections:.1f} average",
                    monthly_savings=monthly_savings,
                    recommendation="Review if database is actively used or consider consolidating databases",
                    severity=severity,
                    metadata={
                        'db_class': db_class,
                        'engine': db_instance.get('Engine', ''),
                        'region': region,
                        'avg_connections': round(avg_connections, 2),
                        'days_analyzed': self.config.get('days_to_check', 14)
                    }
                ))
        
        return findings