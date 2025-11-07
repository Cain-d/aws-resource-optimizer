"""
EBS Scanner - Identifies unattached and underutilized EBS volumes.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any

from .base_scanner import BaseScanner


class EBSScanner(BaseScanner):
    """Scanner for EBS volumes to identify unattached and underutilized storage."""
    
    def scan(self) -> List[Dict[str, Any]]:
        """
        Scan EBS volumes for unattached and underutilized resources.
        
        Returns:
            List of findings
        """
        findings = []
        
        try:
            # Get all regions if not specified
            regions = self.aws_client.get_regions('ec2') if not self.aws_client.region else [self.aws_client.region]
            
            for region in regions:
                self.logger.info(f"Scanning EBS volumes in region: {region}")
                regional_ec2 = self.aws_client.get_client('ec2', region)
                
                # Get all EBS volumes
                paginator = regional_ec2.get_paginator('describe_volumes')
                
                for page in paginator.paginate():
                    for volume in page['Volumes']:
                        volume_findings = self._analyze_volume(volume, region)
                        findings.extend(volume_findings)
                        
        except Exception as e:
            self.logger.error(f"Error scanning EBS volumes: {str(e)}")
            
        return findings
    
    def _analyze_volume(self, volume: Dict[str, Any], region: str) -> List[Dict[str, Any]]:
        """
        Analyze a single EBS volume for issues.
        
        Args:
            volume: EBS volume data
            region: AWS region
            
        Returns:
            List of findings for this volume
        """
        findings = []
        volume_id = volume['VolumeId']
        volume_type = volume['VolumeType']
        volume_size = volume['Size']
        state = volume['State']
        
        # Check if volume should be excluded
        tags = volume.get('Tags', [])
        if self.should_exclude_resource(tags):
            self.logger.debug(f"Excluding volume {volume_id} due to tags")
            return findings
        
        # Check if volume type should be analyzed
        include_types = self.config.get('include_volume_types', ['gp2', 'gp3', 'io1', 'io2'])
        if volume_type not in include_types:
            return findings
        
        # Check for unattached volumes
        if state == 'available':  # Available means unattached
            findings.append(self._create_unattached_volume_finding(volume, region))
        
        # Check for attached volumes with low utilization
        elif state == 'in-use':
            utilization_findings = self._check_volume_utilization(volume, region)
            findings.extend(utilization_findings)
        
        return findings
    
    def _create_unattached_volume_finding(self, volume: Dict[str, Any], region: str) -> Dict[str, Any]:
        """Create finding for unattached volume."""
        volume_id = volume['VolumeId']
        volume_type = volume['VolumeType']
        volume_size = volume['Size']
        
        # Calculate monthly cost based on volume type and size
        monthly_cost = self._calculate_volume_cost(volume_type, volume_size, region)
        
        # Check how long it's been unattached
        create_time = volume.get('CreateTime')
        days_unattached = 0
        if create_time:
            days_unattached = (datetime.utcnow() - create_time.replace(tzinfo=None)).days
        
        severity = 'high' if days_unattached > 30 else 'medium'
        
        return self.create_finding(
            resource_id=volume_id,
            resource_type='EBS',
            issue_type='unattached_volume',
            description=f"EBS volume {volume_id} ({volume_size}GB {volume_type}) is unattached for {days_unattached} days",
            monthly_savings=monthly_cost,
            recommendation="Delete if no longer needed, or attach to an instance if required",
            severity=severity,
            metadata={
                'volume_type': volume_type,
                'volume_size': volume_size,
                'region': region,
                'days_unattached': days_unattached,
                'create_time': create_time.isoformat() if create_time else None
            }
        )
    
    def _check_volume_utilization(self, volume: Dict[str, Any], region: str) -> List[Dict[str, Any]]:
        """
        Check volume utilization for attached volume.
        
        Args:
            volume: EBS volume data
            region: AWS region
            
        Returns:
            List of findings related to volume utilization
        """
        findings = []
        volume_id = volume['VolumeId']
        volume_type = volume['VolumeType']
        volume_size = volume['Size']
        
        # Get volume read/write operations
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=self.config.get('days_to_check', 7))
        
        dimensions = [
            {'Name': 'VolumeId', 'Value': volume_id}
        ]
        
        # Check read operations
        read_ops = self.get_cloudwatch_metrics(
            namespace='AWS/EBS',
            metric_name='VolumeReadOps',
            dimensions=dimensions,
            start_time=start_time,
            end_time=end_time,
            statistic='Sum'
        )
        
        # Check write operations
        write_ops = self.get_cloudwatch_metrics(
            namespace='AWS/EBS',
            metric_name='VolumeWriteOps',
            dimensions=dimensions,
            start_time=start_time,
            end_time=end_time,
            statistic='Sum'
        )
        
        if read_ops or write_ops:
            total_read_ops = sum(read_ops) if read_ops else 0
            total_write_ops = sum(write_ops) if write_ops else 0
            total_ops = total_read_ops + total_write_ops
            
            # Calculate daily average operations
            days_checked = self.config.get('days_to_check', 7)
            daily_avg_ops = total_ops / days_checked if days_checked > 0 else 0
            
            iops_threshold = self.config.get('iops_threshold', 1)
            
            if daily_avg_ops < iops_threshold:
                monthly_cost = self._calculate_volume_cost(volume_type, volume_size, region)
                
                severity = 'medium' if daily_avg_ops == 0 else 'low'
                
                findings.append(self.create_finding(
                    resource_id=volume_id,
                    resource_type='EBS',
                    issue_type='low_volume_utilization',
                    description=f"EBS volume {volume_id} has low utilization: {daily_avg_ops:.1f} operations/day average",
                    monthly_savings=monthly_cost * 0.5,  # Partial savings - might be needed
                    recommendation="Review if volume is needed or consider smaller volume size",
                    severity=severity,
                    metadata={
                        'volume_type': volume_type,
                        'volume_size': volume_size,
                        'region': region,
                        'daily_avg_operations': round(daily_avg_ops, 2),
                        'total_read_ops': total_read_ops,
                        'total_write_ops': total_write_ops,
                        'days_analyzed': days_checked
                    }
                ))
        
        return findings
    
    def _calculate_volume_cost(self, volume_type: str, size_gb: int, region: str) -> float:
        """
        Calculate monthly cost for EBS volume.
        
        Args:
            volume_type: EBS volume type
            size_gb: Volume size in GB
            region: AWS region
            
        Returns:
            Monthly cost in USD
        """
        # Simplified pricing - in production, use AWS Pricing API
        pricing_per_gb = {
            'gp2': 0.10,
            'gp3': 0.08,
            'io1': 0.125,
            'io2': 0.125,
            'st1': 0.045,
            'sc1': 0.025
        }
        
        price_per_gb = pricing_per_gb.get(volume_type, 0.10)
        return size_gb * price_per_gb