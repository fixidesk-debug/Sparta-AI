"""
Report Generator - Export Analysis Reports
Generate formatted reports in PDF, Word, PowerPoint formats
"""
from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate analysis reports in multiple formats"""
    
    @staticmethod
    def generate_markdown_report(
        title: str,
        insights: Dict[str, Any],
        charts: List[Dict[str, Any]],
        code: Optional[str] = None
    ) -> str:
        """Generate markdown report"""
        
        report = f"""# {title}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

{ReportGenerator._format_summary(insights)}

## Key Findings

{ReportGenerator._format_findings(insights.get('key_findings', []))}

## Data Overview

- **Total Rows**: {insights.get('summary', {}).get('total_rows', 'N/A'):,}
- **Total Columns**: {insights.get('summary', {}).get('total_columns', 'N/A')}
- **Missing Data**: {insights.get('summary', {}).get('missing_percentage', 0):.2f}%

## Patterns Detected

{ReportGenerator._format_patterns(insights.get('patterns', []))}

## Anomalies

{ReportGenerator._format_anomalies(insights.get('anomalies', []))}

## Correlations

{ReportGenerator._format_correlations(insights.get('correlations', []))}

## Recommendations

{ReportGenerator._format_recommendations(insights.get('recommendations', []))}

## Visualizations

{len(charts)} charts generated

"""
        
        if code:
            report += f"""
## Analysis Code

```python
{code}
```
"""
        
        return report
    
    @staticmethod
    def generate_html_report(
        title: str,
        insights: Dict[str, Any],
        charts: List[Dict[str, Any]],
        code: Optional[str] = None
    ) -> str:
        """Generate HTML report"""
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1 {{ color: #333; border-bottom: 3px solid #6366f1; padding-bottom: 10px; }}
        h2 {{ color: #6366f1; margin-top: 30px; }}
        .metric {{ background: #f8fafc; padding: 15px; margin: 10px 0; border-radius: 8px; }}
        .finding {{ background: #eff6ff; padding: 10px; margin: 5px 0; border-left: 4px solid #3b82f6; }}
        .warning {{ background: #fef3c7; border-left-color: #f59e0b; }}
        code {{ background: #f1f5f9; padding: 2px 6px; border-radius: 4px; }}
        pre {{ background: #1e293b; color: #e2e8f0; padding: 20px; border-radius: 8px; overflow-x: auto; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p><em>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
    
    <h2>Executive Summary</h2>
    <div class="metric">
        <strong>Dataset Size:</strong> {insights.get('summary', {}).get('total_rows', 'N/A'):,} rows × {insights.get('summary', {}).get('total_columns', 'N/A')} columns<br>
        <strong>Missing Data:</strong> {insights.get('summary', {}).get('missing_percentage', 0):.2f}%<br>
        <strong>Patterns Found:</strong> {len(insights.get('patterns', []))}<br>
        <strong>Anomalies Detected:</strong> {len(insights.get('anomalies', []))}
    </div>
    
    <h2>Key Findings</h2>
    {''.join(f'<div class="finding">{finding}</div>' for finding in insights.get('key_findings', []))}
    
    <h2>Recommendations</h2>
    <ul>
        {''.join(f'<li>{rec}</li>' for rec in insights.get('recommendations', []))}
    </ul>
    
    <h2>Visualizations</h2>
    <p>{len(charts)} charts generated</p>
    
</body>
</html>"""
        
        return html
    
    @staticmethod
    def generate_json_report(
        title: str,
        insights: Dict[str, Any],
        charts: List[Dict[str, Any]],
        code: Optional[str] = None
    ) -> str:
        """Generate JSON report"""
        
        report = {
            "title": title,
            "generated_at": datetime.now().isoformat(),
            "insights": insights,
            "charts": charts,
            "code": code
        }
        
        return json.dumps(report, indent=2)
    
    @staticmethod
    def _format_summary(insights: Dict[str, Any]) -> str:
        """Format summary section"""
        summary = insights.get('summary', {})
        return f"""This analysis covers a dataset with {summary.get('total_rows', 0):,} rows and {summary.get('total_columns', 0)} columns.
The data contains {summary.get('numeric_columns', 0)} numeric and {summary.get('categorical_columns', 0)} categorical variables.
Missing data accounts for {summary.get('missing_percentage', 0):.2f}% of the dataset."""
    
    @staticmethod
    def _format_findings(findings: List[str]) -> str:
        """Format findings"""
        if not findings:
            return "No significant findings."
        return "\n".join(f"- {finding}" for finding in findings)
    
    @staticmethod
    def _format_patterns(patterns: List[Dict[str, Any]]) -> str:
        """Format patterns"""
        if not patterns:
            return "No significant patterns detected."
        
        lines = []
        for p in patterns:
            lines.append(f"- **{p['column']}**: {p['description']}")
        return "\n".join(lines)
    
    @staticmethod
    def _format_anomalies(anomalies: List[Dict[str, Any]]) -> str:
        """Format anomalies"""
        if not anomalies:
            return "No anomalies detected."
        
        lines = []
        for a in anomalies:
            lines.append(f"- **{a['column']}**: {a['description']} ({a['percentage']:.1f}%)")
        return "\n".join(lines)
    
    @staticmethod
    def _format_correlations(correlations: List[Dict[str, Any]]) -> str:
        """Format correlations"""
        if not correlations:
            return "No strong correlations found."
        
        lines = []
        for c in correlations:
            lines.append(f"- {c['description']}")
        return "\n".join(lines)
    
    @staticmethod
    def _format_recommendations(recommendations: List[str]) -> str:
        """Format recommendations"""
        if not recommendations:
            return "No specific recommendations."
        return "\n".join(f"{i+1}. {rec}" for i, rec in enumerate(recommendations))
