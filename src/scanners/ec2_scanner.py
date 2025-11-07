"""
EC2 Instance Scanner - Identifies idle and underutilized EC2 instances.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any

from .base_scanner import BaseScanner


class EC2Scanner(BaseScanner):
    """Scanner for EC2 instances to identify idle and underutilized resources."""
    
    def scan(self) -> List[Dict[str, Any]]:
        """
        Scan EC2 instances for idle and underutilized resources.
        
        Returns:
            List of findings
        """
        findings = []
        
        try:
            ec2 = self.aws_client.get_client('ec2')
            
            # Get all regions if not specified
            regions = self.aws_client.get_regions() if not self.aws_client.region else [self.aws_client.region]
            
            for region in regions:
                self.logger.info(f"Scanning EC2 instances in region: {region}")
                regional_ec2 = self.aws_client.get_client('ec2', region)
                
                # Get all instances
                paginator = regional_ec2.get_paginator('describe_instances')
                
                for page in paginator.paginate():
                    for reservation in page['Reservations']:
                        for instance in reservation['Instances']:
                            instance_findings = self._analyze_instance(instance, region)
                            findings.extend(instance_findings)
                            
        except Exception as e:
            self.logger.error(f"Error scanning EC2 instances: {str(e)}")
            
        return findings
    
    def _analyze_instance(self, instance: Dict[str, Any], region: str) -> List[Dict[str, Any]]:
        """
        Analyze a single EC2 instance for issues.
        
        Args:
            instance: EC2 instance data
            region: AWS region
            
        Returns:
            List of findings for this instance
        """
        findings = []
        instance_id = instance['InstanceId']
        instance_type = instance['InstanceType']
        state = instance['State']['Name']
        
        # Skip terminated instances
        if state == 'terminated':
            return findings
        
        # Check if instance should be excluded
        tags = instance.get('Tags', [])
        if self.should_exclude_resource(tags):
            self.logger.debug(f"Excluding instance {instance_id} due to tags")
            return findings
        
        # Skip excluded instance types
        exclude_types = self.config.get('exclude_instance_types', [])
        if instance_type in exclude_types:
            return findings
        
        # Check for stopped instances
        if state == 'stopped':
            findings.append(self._create_stopped_instance_finding(instance, region))
        
        # Check for running instances with low utilization
        elif state == 'running':
            cpu_findings = self._check_cpu_utilization(instance, region)
            findings.extend(cpu_findings)
            
        return findings
    
    def _create_stopped_instance_finding(self, instance: Dict[str, Any], region: str) -> Dict[str, Any]:
        """Create finding for stopped instance."""
        instance_id = instance['InstanceId']
        instance_type = instance['InstanceType']
        
        # Calculate potential savings (stopped instances still incur EBS costs)
        monthly_savings = self.calculate_cost_savings('ec2', instance_type, region)
        
        return self.create_finding(
            resource_id=instance_id,
            resource_type='EC2',
            issue_type='stopped_instance',
            description=f"EC2 instance {instance_id} ({instance_type}) has been stopped",
            monthly_savings=monthly_savings,
            recommendation="Consider terminating if no longer needed, or start if required",
            severity='medium',
            metadata={
                'instance_type': instance_type,
                'region': region,
                'launch_time': instance.get('LaunchTime', '').isoformat() if instance.get('LaunchTime') else None
            }
        )
    
    def _check_cpu_utilization(self, instance: Dict[str, Any], region: str) -> List[Dict[str, Any]]:
        """
        Check CPU utilization for running instance.
        
        Args:
            instance: EC2 instance data
            region: AWS region
            
        Returns:
            List of findings related to CPU utilization
        """
        findings = []
        instance_id = instance['InstanceId']
        instance_type = instance['InstanceType']
        
        # Get CPU utilization metrics
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=self.config.get('days_to_check', 14))
        
        dimensions = [
            {'Name': 'InstanceId', 'Value': instance_id}
        ]
        
        cpu_values = self.get_cloudwatch_metrics(
            namespace='AWS/EC2',
            metric_name='CPUUtilization',
            dimensions=dimensions,
            start_time=start_time,
            end_time=end_time
        )
        
        if cpu_values:
            avg_cpu = sum(cpu_values) / len(cpu_values)
            max_cpu = max(cpu_values)
            
            cpu_threshold = self.config.get('cpu_threshold', 5)
            
            if avg_cpu < cpu_threshold:
                monthly_savings = self.calculate_cost_savings('ec2', instance_type, region)
                
                severity = 'high' if avg_cpu < 1 else 'medium'
                
                findings.append(self.create_finding(
                    resource_id=instance_id,
                    resource_type='EC2',
                    issue_type='low_cpu_utilization',
                    description=f"EC2 instance {instance_id} has low CPU utilization: {avg_cpu:.1f}% average",
                    monthly_savings=monthly_savings,
                    recommendation=f"Consider downsizing to smaller instance type or terminating if unused",
                    severity=severity,
                    metadata={
                        'instance_type': instance_type,
                        'region': region,
                        'avg_cpu_utilization': round(avg_cpu, 2),
                        'max_cpu_utilization': round(max_cpu, 2),
                        'days_analyzed': self.config.get('days_to_check', 14),
                        'launch_time': instance.get('LaunchTime', '').isoformat() if instance.get('LaunchTime') else None
                    }
                ))
        else:
            # No metrics available - might be a very new instance or metrics disabled
            self.logger.warning(f"No CPU metrics available for instance {instance_id}")
            
        return findings