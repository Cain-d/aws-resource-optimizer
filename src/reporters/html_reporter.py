"""
HTML Reporter - Generates HTML format reports with visualizations.
"""

import logging
from typing import Dict, Any
from pathlib import Path
from datetime import datetime


class HTMLReporter:
    """Generates reports in HTML format."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_report(self, report_data: Dict[str, Any], output_path: str) -> None:
        """
        Generate HTML report.
        
        Args:
            report_data: Report data dictionary
            output_path: Path to save the report
        """
        try:
            # Ensure output directory exists
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate HTML content
            html_content = self._generate_html(report_data)
            
            # Write HTML report
            with open(output_file, 'w') as f:
                f.write(html_content)
            
            self.logger.info(f"HTML report generated: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error generating HTML report: {str(e)}")
            raise
    
    def _generate_html(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML content from report data."""
        findings = report_data.get('findings', [])
        total_savings = report_data.get('total_potential_savings', 0)
        scan_time = report_data.get('scan_timestamp', datetime.utcnow().isoformat())
        
        # Group findings by service
        findings_by_service = {}
        for finding in findings:
            service = finding.get('resource_type', 'Unknown')
            if service not in findings_by_service:
                findings_by_service[service] = []
            findings_by_service[service].append(finding)
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AWS Resource Optimizer Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .summary {{ display: flex; justify-content: space-around; margin-bottom: 30px; }}
        .summary-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; min-width: 150px; }}
        .summary-card h3 {{ margin: 0; color: #333; }}
        .summary-card .value {{ font-size: 2em; font-weight: bold; color: #28a745; }}
        .service-section {{ margin-bottom: 30px; }}
        .service-header {{ background: #007bff; color: white; padding: 10px; border-radius: 4px; }}
        .finding {{ background: #f8f9fa; margin: 10px 0; padding: 15px; border-left: 4px solid #007bff; }}
        .finding.high {{ border-left-color: #dc3545; }}
        .finding.medium {{ border-left-color: #ffc107; }}
        .finding.low {{ border-left-color: #28a745; }}
        .finding-header {{ display: flex; justify-content: space-between; align-items: center; }}
        .resource-id {{ font-family: monospace; background: #e9ecef; padding: 2px 6px; border-radius: 3px; }}
        .savings {{ font-weight: bold; color: #28a745; }}
        .recommendation {{ margin-top: 10px; padding: 10px; background: #e7f3ff; border-radius: 4px; }}
        .metadata {{ margin-top: 10px; font-size: 0.9em; color: #666; }}
        .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 AWS Resource Optimizer Report</h1>
            <p>Generated on {scan_time}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>Total Findings</h3>
                <div class="value">{len(findings)}</div>
            </div>
            <div class="summary-card">
                <h3>Potential Monthly Savings</h3>
                <div class="value">${total_savings:.2f}</div>
            </div>
            <div class="summary-card">
                <h3>Services Analyzed</h3>
                <div class="value">{len(findings_by_service)}</div>
            </div>
        </div>
"""
        
        # Add findings by service
        for service, service_findings in findings_by_service.items():
            service_savings = sum(f.get('monthly_savings', 0) for f in service_findings)
            
            html += f"""
        <div class="service-section">
            <div class="service-header">
                <h2>{service} - {len(service_findings)} findings (${service_savings:.2f}/month potential savings)</h2>
            </div>
"""
            
            for finding in service_findings:
                severity = finding.get('severity', 'medium')
                resource_id = finding.get('resource_id', 'Unknown')
                description = finding.get('description', '')
                monthly_savings = finding.get('monthly_savings', 0)
                recommendation = finding.get('recommendation', '')
                metadata = finding.get('metadata', {})
                
                html += f"""
            <div class="finding {severity}">
                <div class="finding-header">
                    <span class="resource-id">{resource_id}</span>
                    <span class="savings">${monthly_savings:.2f}/month</span>
                </div>
                <p>{description}</p>
"""
                
                if recommendation:
                    html += f"""
                <div class="recommendation">
                    <strong>💡 Recommendation:</strong> {recommendation}
                </div>
"""
                
                if metadata:
                    html += '<div class="metadata"><strong>Details:</strong> '
                    for key, value in metadata.items():
                        if key not in ['region']:  # Skip some metadata
                            html += f"{key}: {value}, "
                    html = html.rstrip(', ') + '</div>'
                
                html += '</div>'
            
            html += '</div>'
        
        html += f"""
        <div class="footer">
            <p>Report generated by AWS Resource Optimizer</p>
            <p>This tool identifies idle and underutilized AWS resources to help optimize costs.</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html