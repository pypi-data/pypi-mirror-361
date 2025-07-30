"""
LLM Code Analyzer Module

This module provides the main functionality for analyzing code using LLMs.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union

import openai
from anthropic import Anthropic
from dotenv import load_dotenv

from .models.analysis_result import AnalysisResult, Issue, Location, Severity
from .prompt import PromptTemplate, get_default_prompt
from .utils.file_filter import get_analyzeable_files, get_file_language


class CodeAnalyzer:
    """Main class for analyzing code using LLMs."""

    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-4",
        prompt: Optional[PromptTemplate] = None,
        api_key: Optional[str] = None,
    ):
        """Initialize the code analyzer.

        Args:
            provider: The LLM provider to use ("openai" or "anthropic")
            model: The model to use for analysis
            prompt: Custom prompt template (optional)
            api_key: API key for the provider (optional)
        """
        print(f"DEBUG: Initializing CodeAnalyzer with provider={provider}, model={model}")
        load_dotenv()

        self.provider = provider.lower()
        self.model = model
        self.prompt = prompt or get_default_prompt()

        # Set up API client
        if self.provider == "openai":
            api_key_to_use = api_key or os.getenv("OPENAI_API_KEY")
            print(f"DEBUG: Using OpenAI API key: {'Provided' if api_key else 'From env'}")
            print(f"DEBUG: API key length: {len(api_key_to_use) if api_key_to_use else 0}")
            if not api_key_to_use:
                raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
            self.client = openai.OpenAI(api_key=api_key_to_use)
            print("DEBUG: OpenAI client initialized successfully")
        elif self.provider == "anthropic":
            api_key_to_use = api_key or os.getenv("ANTHROPIC_API_KEY")
            print(f"DEBUG: Using Anthropic API key: {'Provided' if api_key else 'From env'}")
            if not api_key_to_use:
                raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable or pass api_key parameter.")
            self.client = Anthropic(api_key=api_key_to_use)
            print("DEBUG: Anthropic client initialized successfully")
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def analyze_file(self, file_path: Union[str, Path]) -> AnalysisResult:
        """Analyze a single file.

        Args:
            file_path: Path to the file to analyze

        Returns:
            AnalysisResult containing the analysis results
        """
        print(f"DEBUG: analyze_file called with {file_path}")
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        print(f"DEBUG: Reading file {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        print(f"DEBUG: File read successfully, {len(code)} characters")

        print("DEBUG: Calling analyze_code...")
        result = self.analyze_code(code, str(file_path))
        print(f"DEBUG: analyze_code completed, found {len(result.issues)} issues")
        return result
        
    def analyze_directory(self, directory_path: Union[str, Path]) -> AnalysisResult:
        """Analyze all supported files in a directory recursively.

        Args:
            directory_path: Path to the directory to analyze

        Returns:
            AnalysisResult containing the analysis results for all files
        """
        directory_path = Path(directory_path)
        if not directory_path.exists() or not directory_path.is_dir():
            raise NotADirectoryError(f"Directory not found: {directory_path}")
            
        # Find all analyzeable files in the directory
        analyzeable_files = get_analyzeable_files(directory_path)
        
        if not analyzeable_files:
            print(f"No analyzeable files found in {directory_path}")
            return AnalysisResult()
            
        # Analyze each file and combine results
        combined_result = AnalysisResult()
        for file_path in analyzeable_files:
            try:
                language = get_file_language(file_path)
                print(f"Analyzing {file_path} ({language})...")
                file_result = self.analyze_file(file_path)
                combined_result.issues.extend(file_result.issues)
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
                
        return combined_result

    def analyze_code(self, code: str, file_path: str) -> AnalysisResult:
        """Analyze a code string.

        Args:
            code: The code to analyze
            file_path: Path to the file (for reference)

        Returns:
            AnalysisResult containing the analysis results
        """
        print(f"DEBUG: analyze_code called for {file_path}")
        print(f"DEBUG: Code length: {len(code)} characters")
        
        # Add line numbers to the code for better accuracy
        lines = code.split('\n')
        numbered_code = '\n'.join(f"{i+1:3d}: {line}" for i, line in enumerate(lines))
        
        # Add context about the file being analyzed
        context = f"Analyzing file: {file_path}\n\nCode to analyze (with line numbers):\n{numbered_code}"
        
        # Format the prompt
        prompt = self.prompt.format(code=context)
        print(f"DEBUG: Prompt length: {len(prompt)} characters")

        # Get analysis from LLM
        print(f"DEBUG: Making LLM API call to {self.provider}...")
        try:
            if self.provider == "openai":
                print(f"DEBUG: Using OpenAI model: {self.model}")
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0,
                )
                analysis_text = response.choices[0].message.content
                print(f"DEBUG: OpenAI response received, length: {len(analysis_text)}")
            else:  # anthropic
                print(f"DEBUG: Using Anthropic model: {self.model}")
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4000,
                    messages=[{"role": "user", "content": prompt}],
                )
                analysis_text = response.content[0].text
                print(f"DEBUG: Anthropic response received, length: {len(analysis_text)}")
        except Exception as e:
            print(f"DEBUG: LLM API call failed: {str(e)}")
            raise

        # Parse the response
        print(f"DEBUG: Raw LLM response (first 200 chars): {analysis_text[:200]}...")
        try:
            issues = json.loads(analysis_text)
            if not isinstance(issues, list):
                issues = [issues]
            print(f"DEBUG: Successfully parsed JSON, found {len(issues)} issues")
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON decode error: {e}")
            # If the response is not valid JSON, try to extract JSON objects
            issues = self._extract_json_objects(analysis_text)
            print(f"DEBUG: Extracted {len(issues)} JSON objects from text")

        # Convert to AnalysisResult
        result = AnalysisResult()
        for i, issue in enumerate(issues):
            try:
                # Use flexible parsing that can handle different formats
                parsed_issue = Issue(
                    check_id=issue.get("check_id", f"issue-{i}"),
                    message=issue.get("message") or issue.get("extra", {}).get("message") or issue.get("issue", "Unknown issue"),
                    severity=Severity(issue.get("severity") or issue.get("extra", {}).get("severity") or "WARNING"),
                    location=Location(
                        path=issue.get("path", "unknown.py"),
                        start_line=issue.get("line") or issue.get("start", {}).get("line", 1),
                        end_line=issue.get("line") or issue.get("end", {}).get("line", 1),
                        start_column=issue.get("start", {}).get("col"),
                        end_column=issue.get("end", {}).get("col"),
                    ),
                    description=issue.get("description") or issue.get("extra", {}).get("metadata", {}).get("description", "No description"),
                    recommendation=issue.get("recommendation") or issue.get("extra", {}).get("metadata", {}).get("recommendation", "No recommendation"),
                    code_snippet=issue.get("code") or issue.get("extra", {}).get("lines", "No code snippet"),
                    metadata=issue.get("extra", {}).get("metadata", {}) if "extra" in issue else {}
                )
                result.add_issue(parsed_issue)
            except (KeyError, ValueError) as e:
                print(f"Error parsing issue {i}: {e}")
                print(f"Issue data: {issue}")
                continue

        return result

    def _extract_json_objects(self, text: str) -> List[Dict]:
        """Extract JSON objects from text that might contain multiple objects.

        Args:
            text: Text containing JSON objects

        Returns:
            List of parsed JSON objects
        """
        print(f"DEBUG: Extracting JSON objects from text of length {len(text)}")
        objects = []
        current_object = ""
        brace_count = 0
        in_string = False
        escape_next = False

        for char in text:
            if escape_next:
                current_object += char
                escape_next = False
                continue
                
            if char == '\\':
                escape_next = True
                current_object += char
                continue
                
            if char == '"' and not escape_next:
                in_string = not in_string
                
            if not in_string:
                if char == "{":
                    brace_count += 1
                    current_object += char
                elif char == "}":
                    brace_count -= 1
                    current_object += char
                    if brace_count == 0:
                        try:
                            parsed = json.loads(current_object)
                            objects.append(parsed)
                        except json.JSONDecodeError as e:
                            print(f"DEBUG: Failed to parse JSON object: {e}")
                        current_object = ""
                elif brace_count > 0:
                    current_object += char
            else:
                if brace_count > 0:
                    current_object += char

        print(f"DEBUG: Extracted {len(objects)} valid JSON objects")
        return objects 