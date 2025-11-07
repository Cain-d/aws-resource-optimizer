"""
AWS Client Manager - Handles AWS SDK client creation and configuration.
"""

import boto3
import logging
from typing import Optional, List, Dict, Any
from botocore.exceptions import ClientError, NoCredentialsError


class AWSClientManager:
    """Manages AWS SDK clients with proper configuration and error handling."""
    
    def __init__(self, profile: Optional[str] = None, region: Optional[str] = None, 
                 local_mode: bool = False):
        """
        Initialize AWS client manager.
        
        Args:
            profile: AWS profile name to use
            region: AWS region to use
            local_mode: Use LocalStack for local development
        """
        self.profile = profile
        self.region = region
        self.local_mode = local_mode
        self.logger = logging.getLogger(__name__)
        
        # Initialize session
        self.session = self._create_session()
        
        # Cache for clients
        self._clients = {}
        
    def _create_session(self) -> boto3.Session:
        """Create boto3 session with appropriate configuration."""
        try:
            if self.local_mode:
                # LocalStack configuration
                session = boto3.Session()
                self.logger.info("Using LocalStack for local development")
            elif self.profile:
                session = boto3.Session(profile_name=self.profile)
                self.logger.info(f"Using AWS profile: {self.profile}")
            else:
                session = boto3.Session()
                self.logger.info("Using default AWS credentials")
                
            return session
            
        except Exception as e:
            self.logger.error(f"Error creating AWS session: {str(e)}")
            raise
    
    def get_client(self, service_name: str, region: Optional[str] = None) -> Any:
        """
        Get AWS service client.
        
        Args:
            service_name: AWS service name (e.g., 'ec2', 'rds')
            region: Override region for this client
            
        Returns:
            AWS service client
        """
        client_region = region or self.region or 'us-east-1'
        client_key = f"{service_name}_{client_region}"
        
        if client_key not in self._clients:
            try:
                if self.local_mode:
                    # LocalStack endpoints
                    endpoint_url = f"http://localhost:4566"
                    client = self.session.client(
                        service_name,
                        region_name=client_region,
                        endpoint_url=endpoint_url
                    )
                else:
                    client = self.session.client(
                        service_name,
                        region_name=client_region
                    )
                
                self._clients[client_key] = client
                self.logger.debug(f"Created {service_name} client for region {client_region}")
                
            except NoCredentialsError:
                self.logger.error("AWS credentials not found. Please configure your credentials.")
                raise
            except Exception as e:
                self.logger.error(f"Error creating {service_name} client: {str(e)}")
                raise
                
        return self._clients[client_key]
    
    def get_regions(self, service_name: str = 'ec2') -> List[str]:
        """
        Get list of available AWS regions for a service.
        
        Args:
            service_name: AWS service name
            
        Returns:
            List of region names
        """
        try:
            if self.local_mode:
                # Return common regions for LocalStack
                return ['us-east-1', 'us-west-2', 'eu-west-1']
            
            client = self.get_client(service_name)
            response = client.describe_regions()
            return [region['RegionName'] for region in response['Regions']]
            
        except Exception as e:
            self.logger.error(f"Error getting regions: {str(e)}")
            # Return common regions as fallback
            return ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1']
    
    def test_connection(self) -> bool:
        """
        Test AWS connection and credentials.
        
        Returns:
            True if connection successful
        """
        try:
            sts = self.get_client('sts')
            response = sts.get_caller_identity()
            
            self.logger.info(f"AWS connection successful. Account: {response.get('Account')}")
            return True
            
        except Exception as e:
            self.logger.error(f"AWS connection test failed: {str(e)}")
            return False