from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class Severity(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class Location(BaseModel):
    path: str
    start_line: int
    end_line: int
    start_column: Optional[int] = None
    end_column: Optional[int] = None


class Issue(BaseModel):
    check_id: str
    message: str
    severity: Severity
    location: Location
    description: str
    recommendation: str
    code_snippet: str
    metadata: Dict = Field(default_factory=dict)


class AnalysisResult(BaseModel):
    issues: List[Issue] = Field(default_factory=list)
    summary: Dict = Field(default_factory=dict)
    metadata: Dict = Field(default_factory=dict)

    def add_issue(self, issue: Issue) -> None:
        """Add an issue to the analysis result."""
        self.issues.append(issue)

    def get_issues_by_severity(self, severity: Severity) -> List[Issue]:
        """Get all issues of a specific severity."""
        return [issue for issue in self.issues if issue.severity == severity]

    def to_dict(self) -> Dict:
        """Convert the analysis result to a dictionary."""
        return {
            "issues": [issue.model_dump() for issue in self.issues],
            "summary": self.summary,
            "metadata": self.metadata,
        }

    def to_html(self) -> str:
        """Convert the analysis result to HTML format."""
        from datetime import datetime
        
        # Count issues by severity
        error_count = len(self.get_issues_by_severity(Severity.ERROR))
        warning_count = len(self.get_issues_by_severity(Severity.WARNING))
        info_count = len(self.get_issues_by_severity(Severity.INFO))
        
        # Generate HTML
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CodeCheq Security Analysis Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header .subtitle {{
            margin-top: 10px;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .summary {{
            padding: 30px;
            border-bottom: 1px solid #eee;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            text-align: center;
            border-left: 4px solid #007bff;
        }}
        .summary-card.error {{
            border-left-color: #dc3545;
        }}
        .summary-card.warning {{
            border-left-color: #ffc107;
        }}
        .summary-card.info {{
            border-left-color: #17a2b8;
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            font-size: 2em;
            color: #333;
        }}
        .summary-card p {{
            margin: 0;
            color: #666;
            font-size: 0.9em;
        }}
        .issues {{
            padding: 30px;
        }}
        .issue {{
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            margin-bottom: 20px;
            overflow: hidden;
        }}
        .issue-header {{
            padding: 15px 20px;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .issue-header.error {{
            background: #f8d7da;
            border-color: #f5c6cb;
        }}
        .issue-header.warning {{
            background: #fff3cd;
            border-color: #ffeaa7;
        }}
        .issue-header.info {{
            background: #d1ecf1;
            border-color: #bee5eb;
        }}
        .severity-badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .severity-badge.error {{
            background: #dc3545;
            color: white;
        }}
        .severity-badge.warning {{
            background: #ffc107;
            color: #212529;
        }}
        .severity-badge.info {{
            background: #17a2b8;
            color: white;
        }}
        .issue-content {{
            padding: 20px;
        }}
        .issue-location {{
            font-family: monospace;
            background: #f8f9fa;
            padding: 8px 12px;
            border-radius: 4px;
            margin-bottom: 15px;
            color: #495057;
        }}
        .issue-description {{
            margin-bottom: 15px;
            color: #495057;
        }}
        .issue-recommendation {{
            background: #e7f3ff;
            border-left: 4px solid #007bff;
            padding: 15px;
            margin-bottom: 15px;
        }}
        .issue-recommendation h4 {{
            margin: 0 0 10px 0;
            color: #0056b3;
        }}
        .code-snippet {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            padding: 15px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.9em;
            overflow-x: auto;
            white-space: pre-wrap;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            border-top: 1px solid #e9ecef;
        }}
        .no-issues {{
            text-align: center;
            padding: 60px 20px;
            color: #6c757d;
        }}
        .no-issues h3 {{
            color: #28a745;
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 CodeCheq Security Analysis</h1>
            <div class="subtitle">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
        </div>
        
        <div class="summary">
            <h2>📊 Analysis Summary</h2>
            <div class="summary-grid">
                <div class="summary-card error">
                    <h3>{error_count}</h3>
                    <p>Critical Issues</p>
                </div>
                <div class="summary-card warning">
                    <h3>{warning_count}</h3>
                    <p>Warnings</p>
                </div>
                <div class="summary-card info">
                    <h3>{info_count}</h3>
                    <p>Information</p>
                </div>
                <div class="summary-card">
                    <h3>{len(self.issues)}</h3>
                    <p>Total Issues</p>
                </div>
            </div>
        </div>
        
        <div class="issues">
            <h2>🔍 Detailed Issues</h2>
"""
        
        if not self.issues:
            html += """
            <div class="no-issues">
                <h3>✅ No Security Issues Found</h3>
                <p>Great job! No security vulnerabilities were detected in the analyzed code.</p>
            </div>
"""
        else:
            for i, issue in enumerate(self.issues, 1):
                severity_class = issue.severity.value.lower()
                html += f"""
            <div class="issue">
                <div class="issue-header {severity_class}">
                    <h3>Issue #{i}: {issue.message}</h3>
                    <span class="severity-badge {severity_class}">{issue.severity.value}</span>
                </div>
                <div class="issue-content">
                    <div class="issue-location">
                        📍 {issue.location.path}:{issue.location.start_line}
                        {f':{issue.location.end_line}' if issue.location.end_line != issue.location.start_line else ''}
                    </div>
                    <div class="issue-description">
                        <strong>Description:</strong> {issue.description}
                    </div>
                    <div class="issue-recommendation">
                        <h4>💡 Recommendation</h4>
                        <p>{issue.recommendation}</p>
                    </div>
                    <div class="code-snippet">{issue.code_snippet}</div>
                </div>
            </div>
"""
        
        html += f"""
        </div>
        
        <div class="footer">
            <p>Generated by CodeCheq Security Analyzer</p>
            <p>For more information, visit the CodeCheq documentation</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html

    def to_json(self) -> str:
        """Convert the analysis result to JSON format."""
        return self.model_dump_json(indent=2) 