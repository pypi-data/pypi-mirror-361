#!/usr/bin/env python3
"""
Command Line Interface for AI Code Analyzer
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .main import CodeAnalysisTool
from .utils.config import Config

console = Console()


@click.group()
@click.version_option()
@click.option('--config', '-c', default='config.yaml', help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, config, verbose):
    """AI Code Analyzer - AI-powered code analysis for CI/CD pipelines"""
    ctx.ensure_object(dict)
    ctx.obj['config'] = config
    ctx.obj['verbose'] = verbose
    
    if verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)


@cli.command()
@click.option('--commit', help='Commit hash to analyze')
@click.option('--pr', type=int, help='PR number to analyze')
@click.option('--output', '-o', default='analysis_results.json', help='Output file path')
@click.pass_context
def analyze(ctx, commit, pr, output):
    """Analyze code commits or pull requests"""
    
    if not commit and not pr:
        console.print("[red]Error: Either --commit or --pr must be specified[/red]")
        sys.exit(1)
    
    if commit and pr:
        console.print("[red]Error: Cannot specify both --commit and --pr[/red]")
        sys.exit(1)
    
    config_path = ctx.obj['config']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        task = progress.add_task("Initializing analysis...", total=None)
        
        try:
            tool = CodeAnalysisTool(config_path)
            
            if pr:
                progress.update(task, description=f"Analyzing PR #{pr}...")
                results = asyncio.run(tool.analyze_pr(pr))
            else:
                progress.update(task, description=f"Analyzing commit {commit}...")
                results = asyncio.run(tool.analyze_commit(commit))
            
            progress.update(task, description="Saving results...")
            
            # Save results
            with open(output, "w") as f:
                json.dump(results, f, indent=2)
            
            progress.update(task, description="Analysis complete!")
            
        except Exception as e:
            console.print(f"[red]Analysis failed: {str(e)}[/red]")
            sys.exit(1)
    
    # Display results summary
    _display_results_summary(results)
    
    # Exit with appropriate code based on risk level
    risk_level = results.get("risk_assessment", {}).get("risk_level", "unknown")
    if risk_level in ["high", "critical"]:
        console.print(f"\n[red]Analysis completed with {risk_level} risk level[/red]")
        sys.exit(1)
    else:
        console.print(f"\n[green]Analysis completed successfully[/green]")
        console.print(f"Results saved to: {output}")
        sys.exit(0)


@cli.command()
@click.option('--template', type=click.Choice(['basic', 'advanced', 'enterprise']), 
              default='basic', help='Configuration template to generate')
@click.option('--output', '-o', default='config.yaml', help='Output configuration file')
def init(template, output):
    """Initialize configuration file"""
    
    config_templates = {
        'basic': _get_basic_config_template(),
        'advanced': _get_advanced_config_template(),
        'enterprise': _get_enterprise_config_template()
    }
    
    config_content = config_templates[template]
    
    try:
        with open(output, 'w') as f:
            f.write(config_content)
        
        console.print(f"[green]Configuration file created: {output}[/green]")
        console.print(f"Template: {template}")
        console.print("\n[yellow]Next steps:[/yellow]")
        console.print("1. Edit the configuration file with your settings")
        console.print("2. Set environment variables (GITHUB_TOKEN, OPENAI_API_KEY, etc.)")
        console.print("3. Run: ai-code-analyzer analyze --commit HEAD")
        
    except Exception as e:
        console.print(f"[red]Error creating configuration: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--config', '-c', help='Configuration file to validate')
@click.pass_context
def validate(ctx, config):
    """Validate configuration file"""
    
    config_path = config or ctx.obj['config']
    
    try:
        config_obj = Config(config_path)
        
        # Check required settings
        issues = []
        
        # Check GitHub settings
        if not config_obj.get("github.token") and not config_obj.get("GITHUB_TOKEN"):
            issues.append("GitHub token not configured")
        
        # Check AI settings
        if not config_obj.get("ai.openai_api_key") and not config_obj.get("ai.anthropic_api_key"):
            issues.append("No AI API key configured (OpenAI or Anthropic)")
        
        # Check repository path
        repo_path = config_obj.get("repository.path", ".")
        if not Path(repo_path).exists():
            issues.append(f"Repository path does not exist: {repo_path}")
        
        if issues:
            console.print("[red]Configuration validation failed:[/red]")
            for issue in issues:
                console.print(f"  • {issue}")
            sys.exit(1)
        else:
            console.print("[green]Configuration is valid![/green]")
            
    except Exception as e:
        console.print(f"[red]Error validating configuration: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
def version():
    """Show version information"""
    from . import __version__, __author__
    
    console.print(f"AI Code Analyzer v{__version__}")
    console.print(f"Author: {__author__}")


def _display_results_summary(results):
    """Display analysis results summary"""
    
    # Risk Assessment Panel
    risk_assessment = results.get("risk_assessment", {})
    risk_level = risk_assessment.get("risk_level", "unknown")
    risk_score = risk_assessment.get("risk_score", 0)
    
    risk_colors = {
        "low": "green",
        "medium": "yellow", 
        "high": "red",
        "critical": "bright_red"
    }
    
    risk_color = risk_colors.get(risk_level, "white")
    
    risk_panel = Panel(
        f"[{risk_color}]Risk Level: {risk_level.upper()}[/{risk_color}]\n"
        f"Risk Score: {risk_score:.1f}/100\n"
        f"Confidence: {risk_assessment.get('confidence', 0):.1f}",
        title="🎯 Risk Assessment",
        border_style=risk_color
    )
    
    console.print(risk_panel)
    
    # Metrics Table
    table = Table(title="📊 Analysis Metrics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    
    # Add metrics
    analysis = results.get("analysis", {})
    tests = results.get("tests", {})
    test_summary = tests.get("summary", {})
    
    table.add_row("Code Quality Score", f"{analysis.get('quality_score', 0):.1f}/100")
    table.add_row("Security Issues", str(len(analysis.get('security_issues', []))))
    table.add_row("Performance Issues", str(len(analysis.get('performance_issues', []))))
    table.add_row("Test Coverage", f"{test_summary.get('coverage_percentage', 0):.1f}%")
    table.add_row("Tests Passed", f"{test_summary.get('passed_tests', 0)}/{test_summary.get('total_tests', 0)}")
    
    console.print(table)
    
    # Recommendations
    recommendations = risk_assessment.get("recommendations", [])
    if recommendations:
        console.print("\n[bold]💡 Top Recommendations:[/bold]")
        for i, rec in enumerate(recommendations[:3], 1):
            console.print(f"  {i}. {rec}")


def _get_basic_config_template():
    """Get basic configuration template"""
    return """# AI Code Analyzer Configuration

# Repository settings
repository:
  path: "."

# GitHub integration
github:
  token: "${GITHUB_TOKEN}"
  owner: "${GITHUB_REPOSITORY_OWNER}"
  repo: "${GITHUB_REPOSITORY_NAME}"

# AI model settings
ai:
  openai_api_key: "${OPENAI_API_KEY}"
  model_preference: "openai"

# Load testing
load_testing:
  enabled: false
  host: "http://localhost:8000"

# Risk assessment thresholds
risk_assessment:
  thresholds:
    low: 0
    medium: 40
    high: 60
    critical: 80
"""


def _get_advanced_config_template():
    """Get advanced configuration template"""
    return """# AI Code Analyzer Configuration - Advanced

# Repository settings
repository:
  path: "."

# GitHub integration
github:
  token: "${GITHUB_TOKEN}"
  owner: "${GITHUB_REPOSITORY_OWNER}"
  repo: "${GITHUB_REPOSITORY_NAME}"

# AI model settings
ai:
  openai_api_key: "${OPENAI_API_KEY}"
  anthropic_api_key: "${ANTHROPIC_API_KEY}"
  model_preference: "openai"

# Load testing configuration
load_testing:
  enabled: true
  host: "http://localhost:8000"
  
  basic:
    users: 10
    spawn_rate: 2
    duration: 60
  
  spike:
    users: 50
    spawn_rate: 10
    duration: 30

# Code analysis settings
analysis:
  languages:
    - python
    - javascript
    - typescript
    - java
    - go
  
  security:
    enable_bandit: true
    enable_safety: true
    enable_semgrep: true
    enable_eslint: true
  
  quality:
    min_code_quality_score: 70
    min_test_coverage: 80
    max_cyclomatic_complexity: 15

# Test execution settings
testing:
  frameworks:
    python: ["pytest", "unittest"]
    javascript: ["jest", "mocha"]
  
  coverage:
    min_coverage: 80

# Risk assessment settings
risk_assessment:
  weights:
    security: 0.3
    performance: 0.2
    reliability: 0.25
    maintainability: 0.15
    testing: 0.1
  
  thresholds:
    low: 0
    medium: 40
    high: 60
    critical: 80

# Reporting settings
reporting:
  formats:
    - json
    - html
    - markdown
"""


def _get_enterprise_config_template():
    """Get enterprise configuration template"""
    return """# AI Code Analyzer Configuration - Enterprise

# Repository settings
repository:
  path: "."

# GitHub integration
github:
  token: "${GITHUB_TOKEN}"
  owner: "${GITHUB_REPOSITORY_OWNER}"
  repo: "${GITHUB_REPOSITORY_NAME}"

# AI model settings
ai:
  openai_api_key: "${OPENAI_API_KEY}"
  anthropic_api_key: "${ANTHROPIC_API_KEY}"
  model_preference: "openai"

# Load testing configuration
load_testing:
  enabled: true
  host: "http://localhost:8000"
  
  basic:
    users: 10
    spawn_rate: 2
    duration: 60
  
  spike:
    users: 50
    spawn_rate: 10
    duration: 30
  
  stress:
    users: 100
    spawn_rate: 5
    duration: 300
  
  endurance:
    users: 20
    spawn_rate: 1
    duration: 1800

# Code analysis settings
analysis:
  languages:
    - python
    - javascript
    - typescript
    - java
    - go
    - rust
    - c
    - cpp
    - ruby
    - php
    - swift
    - kotlin
    - scala
  
  security:
    enable_bandit: true
    enable_safety: true
    enable_semgrep: true
    enable_eslint: true
    enable_sonarqube: true
  
  performance:
    enable_profiling: true
    complexity_threshold: 10
    performance_threshold: 1000
  
  quality:
    min_code_quality_score: 80
    min_test_coverage: 85
    max_cyclomatic_complexity: 12

# Test execution settings
testing:
  frameworks:
    python: ["pytest", "unittest"]
    javascript: ["jest", "mocha"]
    java: ["junit", "testng"]
    go: ["go test"]
    rust: ["cargo test"]
  
  test_types:
    - unit
    - integration
    - e2e
    - performance
    - security
  
  coverage:
    min_coverage: 85
    coverage_formats: ["html", "xml", "json"]

# Risk assessment settings
risk_assessment:
  weights:
    security: 0.35
    performance: 0.20
    reliability: 0.25
    maintainability: 0.15
    testing: 0.05
  
  thresholds:
    low: 0
    medium: 30
    high: 50
    critical: 70

# Reporting settings
reporting:
  formats:
    - json
    - html
    - markdown
    - pdf
  
  sections:
    - summary
    - risk_assessment
    - code_quality
    - test_results
    - performance
    - security
    - recommendations
  
  release_notes:
    include_metrics: true
    include_test_results: true
    include_performance: true
    include_security: true
    include_recommendations: true

# Notification settings
notifications:
  slack:
    enabled: false
    webhook_url: "${SLACK_WEBHOOK_URL}"
  
  email:
    enabled: false
    smtp_server: "${SMTP_SERVER}"
    smtp_port: 587
    username: "${SMTP_USERNAME}"
    password: "${SMTP_PASSWORD}"
    recipients: []

# Cache settings
cache:
  enabled: true
  ttl: 3600

# Logging settings
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
"""


def main():
    """Main entry point for CLI"""
    cli()


if __name__ == "__main__":
    main()