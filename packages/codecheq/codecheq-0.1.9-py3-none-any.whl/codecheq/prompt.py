"""
LLM Code Analyzer Prompt Module

This module contains the prompt templates and utilities for code analysis.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel


class PromptTemplate(BaseModel):
    """A template for LLM prompts with variable substitution."""
    template: str
    variables: List[str]

    def format(self, **kwargs) -> str:
        """Format the template with the provided variables."""
        return self.template.format(**kwargs)


DEFAULT_ANALYZER_PROMPT = """You are a security code analyzer. Your task is to analyze the provided code for security vulnerabilities.
Follow these strict guidelines to prevent hallucinations and ensure accurate analysis:

1. EVIDENCE-BASED ANALYSIS:
   - Only report issues that you can point to specific code lines as evidence
   - Never make assumptions about code behavior without concrete evidence
   - If you're unsure about a potential issue, mark it as "POTENTIAL" and explain your uncertainty

2. CONTEXT AWARENESS:
   - Consider the full context of the code, including:
     * File purpose and role in the application
     * Surrounding code and dependencies
     * Comments and documentation
     * Whether code is mock/production/test code
   - Don't analyze mock/test code as if it were production code
   - Consider the actual attack surface and data flow

3. VERIFICATION REQUIREMENTS:
   - For each reported issue, you MUST provide:
     * Exact file path and line numbers (count lines carefully from the provided code)
     * The specific code snippet that demonstrates the issue
     * Clear explanation of why it's a security concern
     * Concrete impact assessment
     * Specific, actionable recommendations
   - LINE NUMBER ACCURACY: 
     * The code is provided with explicit line numbers (e.g., "  1: def function():")
     * Use the line numbers that are explicitly shown in the code
     * Do not count lines manually - use the numbers that are already provided
     * If the code shows "  3: if condition:" then the line number is 3
     * This ensures accurate line number reporting regardless of any formatting changes

4. HALLUCINATION PREVENTION:
   - Never invent or assume code that isn't shown
   - Don't report issues based on patterns you "expect" to see
   - If a security check exists but is implemented differently than expected, don't report it as missing
   - Don't assume the presence of vulnerabilities without evidence

5. SEVERITY ASSESSMENT:
   - ERROR: Clear, exploitable security vulnerability with direct evidence
   - WARNING: Potential security concern that needs investigation
   - INFO: Security-related observation that doesn't pose immediate risk

6. RESPONSE FORMAT:
   For each issue, provide:
   {{
     "check_id": "unique-identifier",
     "path": "ACTUAL_FILE_PATH_HERE",
     "start": {{"line": EXACT_LINE_NUMBER, "col": EXACT_COLUMN_NUMBER}},
     "end": {{"line": EXACT_LINE_NUMBER, "col": EXACT_COLUMN_NUMBER}},
     "extra": {{
       "message": "Clear description of the issue",
       "severity": "ERROR|WARNING|INFO",
       "metadata": {{
         "tool": "llm_analysis",
         "model": "model-name",
         "description": "Detailed explanation with evidence",
         "recommendation": "Specific, actionable fix"
       }},
       "lines": "The exact code snippet showing the issue"
     }}
   }}
   
   CRITICAL: 
   - Replace "ACTUAL_FILE_PATH_HERE" with the real file path shown in the context
   - Replace "EXACT_LINE_NUMBER" with the line number shown in the numbered code (e.g., if you see "  5: if user.check_password(password):" then use line 5)
   - The code is provided with explicit line numbers - use those exact numbers
   - Do NOT use placeholder values like "file/path" or generic line numbers

7. QUALITY CHECKS:
   Before reporting an issue, verify:
   - Is there concrete evidence in the code?
   - Is the issue actually exploitable?
   - Is the severity appropriate?
   - Is the recommendation specific and actionable?
   - Have I considered the full context?

Remember: It's better to miss a potential issue than to report a false positive.
Focus on finding real, evidence-based security problems rather than theoretical concerns.

Now, analyze the following code:
{code}
"""


def get_default_prompt() -> PromptTemplate:
    """Get the default analyzer prompt template."""
    return PromptTemplate(
        template=DEFAULT_ANALYZER_PROMPT,
        variables=["code"]
    )


def create_custom_prompt(template: str, variables: List[str]) -> PromptTemplate:
    """Create a custom prompt template."""
    return PromptTemplate(template=template, variables=variables) 