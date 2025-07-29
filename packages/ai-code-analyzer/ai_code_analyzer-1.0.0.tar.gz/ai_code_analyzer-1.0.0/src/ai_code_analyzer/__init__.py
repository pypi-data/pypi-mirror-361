"""
AI Code Analyzer - AI-powered code analysis tool for CI/CD pipelines
"""

__version__ = "1.0.0"
__author__ = "AI Code Analysis Team"
__email__ = "team@ai-code-analyzer.com"

from .core.analyzer import CodeAnalyzer
from .core.test_executor import TestExecutor
from .core.load_tester import LoadTester
from .core.ai_model import AIRiskAssessment
from .core.release_notes import ReleaseNotesGenerator
from .core.github_integration import GitHubIntegration
from .utils.config import Config
from .main import CodeAnalysisTool

__all__ = [
    "CodeAnalyzer",
    "TestExecutor", 
    "LoadTester",
    "AIRiskAssessment",
    "ReleaseNotesGenerator",
    "GitHubIntegration",
    "Config",
    "CodeAnalysisTool",
]