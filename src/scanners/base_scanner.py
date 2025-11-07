"""
Base scanner class that all service scanners inherit from.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


class BaseScanner(ABC):
    """Base class for all AWS service scanners."""
    
    def __init__(self, aws_client_manager, config: Dict[str, Any]):
        """
        Initialize the scanner.
        
        Args:
            aws_client_manager: AWS client manager instance
            config: Scanner-specific configuration
        """
        self.aws_client = aws_client_manager
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    def scan(self) -> List[Dict[str, Any]]:
        """
        Perform the scan and return findings.
        
        Returns:
            List of findings, each as a dictionary
        """
        pass
    
    def get_cloudwatch_metrics(self, namespace: str, metric_name: str, 
                              dimensions: List[Dict[str, str]], 
                              start_time: datetime, end_time: datetime,
                              statistic: str = 'Average') -> List[float]:
        """
        Get CloudWatch metrics for analysis.
        
        Args:
            namespace: AWS namespace (e.g., 'AWS/EC2')
            metric_name: Metric name (e.g., 'CPUUtilization')
            dimensions: Metric dimensions
            start_time: Start time for metrics
            end_time: End time for metrics
            statistic: Statistic type (Average, Maximum, etc.)
            
        Returns:
            List of metric values
        """
        try:
            cloudwatch = self.aws_client.get_client('cloudwatch')
            
            response = cloudwatch.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric_name,
                Dimensions=dimensions,
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,  # 1 hour periods
                Statistics=[statistic]
            )
            
            return [point[statistic] for point in response['Datapoints']]
            
        except Exception as e:
            self.logger.error(f"Error getting CloudWatch metrics: {str(e)}")
            return []
    
    def calculate_cost_savings(self, resource_type: str, instance_type: str, 
                              region: str, hours_per_month: int = 730) -> float:
        """
        Calculate potential monthly cost savings.
        
        Args:
            resource_type: Type of resource (ec2, rds, etc.)
            instance_type: Instance type (t3.micro, db.t3.micro, etc.)
            region: AWS region
            hours_per_month: Hours per month (default 730)
            
        Returns:
            Monthly cost savings in USD
        """
        # Simplified cost calculation - in production, you'd use AWS Pricing API
        cost_map = {
            'ec2': {
                't2.micro': 0.0116,
                't2.small': 0.023,
                't2.medium': 0.0464,
                't3.micro': 0.0104,
                't3.small': 0.0208,
                't3.medium': 0.0416,
                'm5.large': 0.096,
                'm5.xlarge': 0.192,
            },
            'rds': {
                'db.t3.micro': 0.017,
                'db.t3.small': 0.034,
                'db.t3.medium': 0.068,
                'db.m5.large': 0.192,
                'db.m5.xlarge': 0.384,
            }
        }
        
        hourly_rate = cost_map.get(resource_type, {}).get(instance_type, 0.05)
        return hourly_rate * hours_per_month
    
    def should_exclude_resource(self, tags: List[Dict[str, str]]) -> bool:
        """
        Check if resource should be excluded based on tags.
        
        Args:
            tags: List of resource tags
            
        Returns:
            True if resource should be excluded
        """
        exclude_tags = self.config.get('exclude_tags', [])
        
        for tag in tags:
            key = tag.get('Key', '')
            value = tag.get('Value', '')
            
            for exclude_tag in exclude_tags:
                if isinstance(exclude_tag, dict):
                    for exclude_key, exclude_value in exclude_tag.items():
                        if key == exclude_key and value == str(exclude_value):
                            return True
                elif key == exclude_tag:
                    return True
                    
        return False
    
    def create_finding(self, resource_id: str, resource_type: str, 
                      issue_type: str, description: str, 
                      monthly_savings: float = 0, 
                      recommendation: str = "", 
                      severity: str = "medium",
                      metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a standardized finding dictionary.
        
        Args:
            resource_id: AWS resource identifier
            resource_type: Type of resource (EC2, RDS, etc.)
            issue_type: Type of issue found
            description: Human-readable description
            monthly_savings: Potential monthly savings in USD
            recommendation: Recommended action
            severity: Issue severity (low, medium, high, critical)
            metadata: Additional metadata about the finding
            
        Returns:
            Standardized finding dictionary
        """
        return {
            'resource_id': resource_id,
            'resource_type': resource_type,
            'issue_type': issue_type,
            'description': description,
            'monthly_savings': monthly_savings,
            'recommendation': recommendation,
            'severity': severity,
            'found_at': datetime.utcnow().isoformat(),
            'scanner': self.__class__.__name__,
            'metadata': metadata or {}
        }