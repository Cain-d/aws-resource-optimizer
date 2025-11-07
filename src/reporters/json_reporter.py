"""
JSON Reporter - Generates JSON format reports.
"""

import json
import logging
from typing import Dict, Any
from pathlib import Path


class JSONReporter:
    """Generates reports in JSON format."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_report(self, report_data: Dict[str, Any], output_path: str) -> None:
        """
        Generate JSON report.
        
        Args:
            report_data: Report data dictionary
            output_path: Path to save the report
        """
        try:
            # Ensure output directory exists
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write JSON report
            with open(output_file, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            self.logger.info(f"JSON report generated: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error generating JSON report: {str(e)}")
            raise