"""
Tests for the main application module.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import os

# Add src to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import main
from utils.config_loader import ConfigLoader
from utils.aws_client import AWSClientManager


class TestConfigLoader:
    """Test configuration loading functionality."""
    
    def test_load_default_config(self):
        """Test loading default configuration when file doesn't exist."""
        config = ConfigLoader.load('nonexistent.yaml')
        
        assert 'ec2' in config
        assert 'rds' in config
        assert 'ebs' in config
        assert config['ec2']['cpu_threshold'] == 5
        assert config['rds']['cpu_threshold'] == 10
    
    def test_load_custom_config(self):
        """Test loading custom configuration from file."""
        # Create temporary config file
        config_data = {
            'ec2': {
                'cpu_threshold': 15,
                'days_to_check': 30
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(config_data, f)
            temp_config_path = f.name
        
        try:
            config = ConfigLoader.load(temp_config_path)
            
            # Should have custom values
            assert config['ec2']['cpu_threshold'] == 15
            assert config['ec2']['days_to_check'] == 30
            
            # Should have default values for missing keys
            assert 'minimum_runtime_hours' in config['ec2']
            assert 'rds' in config
            
        finally:
            os.unlink(temp_config_path)


class TestAWSClientManager:
    """Test AWS client management functionality."""
    
    def test_local_mode_initialization(self):
        """Test initialization in local mode."""
        client_manager = AWSClientManager(local_mode=True)
        assert client_manager.local_mode is True
        assert client_manager.session is not None
    
    def test_profile_initialization(self):
        """Test initialization with AWS profile."""
        with patch('boto3.Session') as mock_session:
            client_manager = AWSClientManager(profile='test-profile')
            mock_session.assert_called_with(profile_name='test-profile')
    
    @patch('boto3.Session')
    def test_get_client_local_mode(self, mock_session):
        """Test getting client in local mode."""
        mock_client = Mock()
        mock_session_instance = Mock()
        mock_session_instance.client.return_value = mock_client
        mock_session.return_value = mock_session_instance
        
        client_manager = AWSClientManager(local_mode=True)
        ec2_client = client_manager.get_client('ec2')
        
        mock_session_instance.client.assert_called_with(
            'ec2',
            region_name='us-east-1',
            endpoint_url='http://localhost:4566'
        )
    
    def test_get_regions_local_mode(self):
        """Test getting regions in local mode."""
        client_manager = AWSClientManager(local_mode=True)
        regions = client_manager.get_regions()
        
        assert isinstance(regions, list)
        assert 'us-east-1' in regions
        assert len(regions) > 0


class TestMainApplication:
    """Test main application functionality."""
    
    @patch('sys.argv', ['main.py', '--local', '--output', 'test_output.json'])
    @patch('src.main.AWSClientManager')
    @patch('src.main.ConfigLoader')
    def test_main_local_mode(self, mock_config_loader, mock_aws_client):
        """Test main function in local mode."""
        # Mock configuration
        mock_config = {
            'ec2': {'cpu_threshold': 5, 'days_to_check': 14},
            'rds': {'cpu_threshold': 10, 'days_to_check': 14},
            'ebs': {'days_to_check': 7}
        }
        mock_config_loader.load.return_value = mock_config
        
        # Mock AWS client manager
        mock_client_instance = Mock()
        mock_aws_client.return_value = mock_client_instance
        
        # Mock scanners to return empty findings
        with patch('src.main.EC2Scanner') as mock_ec2_scanner, \
             patch('src.main.RDSScanner') as mock_rds_scanner, \
             patch('src.main.EBSScanner') as mock_ebs_scanner, \
             patch('src.main.JSONReporter') as mock_reporter:
            
            # Configure scanner mocks
            mock_ec2_scanner.return_value.scan.return_value = []
            mock_rds_scanner.return_value.scan.return_value = []
            mock_ebs_scanner.return_value.scan.return_value = []
            
            # Configure reporter mock
            mock_reporter_instance = Mock()
            mock_reporter.return_value = mock_reporter_instance
            
            # Run main function
            try:
                main()
            except SystemExit:
                pass  # Expected for successful completion
            
            # Verify scanners were called
            assert mock_ec2_scanner.called
            assert mock_rds_scanner.called
            assert mock_ebs_scanner.called
            
            # Verify report was generated
            assert mock_reporter_instance.generate_report.called


class TestIntegration:
    """Integration tests with mock AWS services."""
    
    def test_end_to_end_with_mock_findings(self):
        """Test complete workflow with mock findings."""
        # Create temporary output file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_output = f.name
        
        try:
            # Mock findings data
            mock_findings = [
                {
                    'resource_id': 'i-1234567890abcdef0',
                    'resource_type': 'EC2',
                    'issue_type': 'low_cpu_utilization',
                    'description': 'Low CPU utilization',
                    'monthly_savings': 50.0,
                    'severity': 'medium'
                }
            ]
            
            with patch('src.main.EC2Scanner') as mock_scanner, \
                 patch('src.main.RDSScanner'), \
                 patch('src.main.EBSScanner'), \
                 patch('src.main.AWSClientManager'), \
                 patch('src.main.ConfigLoader') as mock_config:
                
                # Configure mocks
                mock_scanner.return_value.scan.return_value = mock_findings
                mock_config.load.return_value = {'ec2': {}, 'rds': {}, 'ebs': {}}
                
                # Import and run with mocked arguments
                import sys
                original_argv = sys.argv
                sys.argv = ['main.py', '--local', '--output', temp_output]
                
                try:
                    main()
                except SystemExit:
                    pass
                finally:
                    sys.argv = original_argv
                
                # Verify output file was created and contains expected data
                assert os.path.exists(temp_output)
                
                with open(temp_output, 'r') as f:
                    report_data = json.load(f)
                
                assert 'findings' in report_data
                assert 'total_potential_savings' in report_data
                assert len(report_data['findings']) > 0
                
        finally:
            if os.path.exists(temp_output):
                os.unlink(temp_output)


if __name__ == '__main__':
    pytest.main([__file__])