"""
Configuration Loader - Handles loading and validation of configuration files.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any


class ConfigLoader:
    """Loads and validates configuration from YAML files."""
    
    @staticmethod
    def load(config_path: str) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        logger = logging.getLogger(__name__)
        
        try:
            config_file = Path(config_path)
            
            if not config_file.exists():
                logger.warning(f"Configuration file not found: {config_path}")
                return ConfigLoader._get_default_config()
            
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            logger.info(f"Loaded configuration from {config_path}")
            
            # Validate and merge with defaults
            return ConfigLoader._validate_config(config)
            
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            raise
    
    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            'ec2': {
                'cpu_threshold': 5,
                'days_to_check': 14,
                'minimum_runtime_hours': 24,
                'exclude_instance_types': ['t2.nano', 't3.nano'],
                'exclude_tags': []
            },
            'rds': {
                'cpu_threshold': 10,
                'connection_threshold': 5,
                'days_to_check': 14,
                'exclude_engines': [],
                'minimum_age_days': 7
            },
            'ebs': {
                'days_to_check': 7,
                'iops_threshold': 1,
                'exclude_tags': [],
                'include_volume_types': ['gp2', 'gp3', 'io1', 'io2']
            },
            'cost_calculation': {
                'pricing_region': 'us-east-1',
                'include_data_transfer': False,
                'currency': 'USD'
            },
            'reporting': {
                'include_recommendations': True,
                'group_by_service': True,
                'include_cost_breakdown': True,
                'max_findings': 0
            }
        }
    
    @staticmethod
    def _validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate configuration and merge with defaults.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Validated configuration
        """
        default_config = ConfigLoader._get_default_config()
        
        # Merge with defaults (config takes precedence)
        for section, default_values in default_config.items():
            if section not in config:
                config[section] = default_values
            else:
                # Merge section-level defaults
                for key, default_value in default_values.items():
                    if key not in config[section]:
                        config[section][key] = default_value
        
        # Validate specific values
        ConfigLoader._validate_thresholds(config)
        
        return config
    
    @staticmethod
    def _validate_thresholds(config: Dict[str, Any]) -> None:
        """Validate threshold values are reasonable."""
        logger = logging.getLogger(__name__)
        
        # Validate EC2 thresholds
        ec2_config = config.get('ec2', {})
        if ec2_config.get('cpu_threshold', 0) > 100:
            logger.warning("EC2 CPU threshold > 100%, setting to 100%")
            ec2_config['cpu_threshold'] = 100
        
        # Validate RDS thresholds
        rds_config = config.get('rds', {})
        if rds_config.get('cpu_threshold', 0) > 100:
            logger.warning("RDS CPU threshold > 100%, setting to 100%")
            rds_config['cpu_threshold'] = 100
        
        # Validate days_to_check values
        for section in ['ec2', 'rds', 'ebs']:
            section_config = config.get(section, {})
            days = section_config.get('days_to_check', 14)
            if days > 90:
                logger.warning(f"{section} days_to_check > 90, setting to 90")
                section_config['days_to_check'] = 90
            elif days < 1:
                logger.warning(f"{section} days_to_check < 1, setting to 1")
                section_config['days_to_check'] = 1