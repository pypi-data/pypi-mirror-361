# 🤖 AI Code Analyzer

[![PyPI version](https://badge.fury.io/py/ai-code-analyzer.svg)](https://badge.fury.io/py/ai-code-analyzer)
[![Python Support](https://img.shields.io/pypi/pyversions/ai-code-analyzer.svg)](https://pypi.org/project/ai-code-analyzer/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Actions](https://github.com/ai-code-analyzer/ai-code-analyzer/workflows/CI/badge.svg)](https://github.com/ai-code-analyzer/ai-code-analyzer/actions)

A comprehensive AI-powered code analysis package that integrates with CI/CD pipelines to analyze code commits, execute tests, perform load testing, and generate detailed release notes with risk assessments.

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install ai-code-analyzer

# Or install with all optional dependencies
pip install ai-code-analyzer[all]
```

### GitHub Action Usage

Add this to your `.github/workflows/ci.yml`:

```yaml
name: AI Code Analysis

on:
  pull_request:
  push:
    branches: [main]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: ai-code-analyzer/ai-code-analyzer@v1
      with:
        github-token: ${{ secrets.GITHUB_TOKEN }}
        openai-api-key: ${{ secrets.OPENAI_API_KEY }}
```

### Command Line Usage

```bash
# Initialize configuration
ai-code-analyzer init

# Analyze a commit
ai-code-analyzer analyze --commit HEAD

# Analyze a pull request
ai-code-analyzer analyze --pr 123

# Validate configuration
ai-code-analyzer validate
```

## 🚀 Features

### Core Analysis Capabilities
- **Multi-language support**: Python, JavaScript/TypeScript, Java, Go, Rust, C/C++, Ruby, PHP, Swift, Kotlin, Scala
- **Static code analysis**: Security vulnerabilities, code quality, complexity metrics
- **Dynamic testing**: Unit tests, integration tests, end-to-end tests
- **Load testing**: Performance testing with Locust and Artillery
- **Security scanning**: Bandit, Safety, Semgrep, and custom security rules
- **AI-powered risk assessment**: Using OpenAI GPT-4 or Anthropic Claude

### CI/CD Integration
- **GitHub Actions**: Automated analysis on PR and push events
- **PR status updates**: Automatic comments and status checks
- **Risk-based deployment**: Blocks high-risk changes from merging
- **Release notes generation**: AI-generated release notes with metrics

### Advanced Features
- **Comprehensive reporting**: JSON, HTML, and Markdown outputs
- **Performance metrics**: Response times, throughput, failure rates
- **Test coverage analysis**: Multi-framework support with detailed reporting
- **Code quality scoring**: Weighted scoring system with customizable thresholds
- **Recommendation engine**: AI-powered suggestions for improvements

## 📦 Package Features

- **Easy Installation**: Available on PyPI with simple `pip install`
- **GitHub Action**: Ready-to-use GitHub Action for seamless CI/CD integration
- **CLI Interface**: Rich command-line interface with beautiful output
- **Configuration Templates**: Pre-built configuration templates for different use cases
- **Extensible**: Modular architecture for easy customization and extension

## 🛠️ Installation Options

### Option 1: PyPI Package (Recommended)

```bash
# Basic installation
pip install ai-code-analyzer

# With development tools
pip install ai-code-analyzer[dev]

# With all optional dependencies
pip install ai-code-analyzer[all]
```

### Option 2: GitHub Action

Create `.github/workflows/ai-analysis.yml`:

```yaml
name: AI Code Analysis

on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: ai-code-analyzer/ai-code-analyzer@v1
      with:
        github-token: ${{ secrets.GITHUB_TOKEN }}
        openai-api-key: ${{ secrets.OPENAI_API_KEY }}
```

### Option 3: From Source

```bash
git clone https://github.com/ai-code-analyzer/ai-code-analyzer.git
cd ai-code-analyzer
pip install -e .
```

## ⚙️ Quick Configuration

### Generate Configuration File

```bash
# Basic configuration
ai-code-analyzer init

# Advanced configuration
ai-code-analyzer init --template advanced

# Enterprise configuration
ai-code-analyzer init --template enterprise
```

### Set Environment Variables

```bash
export GITHUB_TOKEN="your-github-token"
export OPENAI_API_KEY="your-openai-api-key"
# OR
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

## 🎯 GitHub Action Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `github-token` | GitHub token for API access | Yes | `${{ github.token }}` |
| `openai-api-key` | OpenAI API key for AI analysis | No | - |
| `anthropic-api-key` | Anthropic API key for AI analysis | No | - |
| `commit-hash` | Specific commit to analyze | No | Auto-detect |
| `pr-number` | PR number to analyze | No | Auto-detect |
| `config-file` | Configuration file path | No | `.ai-code-analyzer.yml` |
| `load-testing` | Enable load testing | No | `false` |
| `fail-on-high-risk` | Fail on high/critical risk | No | `true` |

## 📊 GitHub Action Outputs

| Output | Description |
|--------|-------------|
| `risk-level` | Overall risk level (low, medium, high, critical) |
| `risk-score` | Risk score (0-100) |
| `code-quality-score` | Code quality score (0-100) |
| `test-coverage` | Test coverage percentage |
| `security-issues` | Number of security issues |
| `performance-issues` | Number of performance issues |
| `analysis-results` | Path to detailed results file |

## 🔧 CLI Commands

### Analyze Code

```bash
# Analyze current commit
ai-code-analyzer analyze --commit HEAD

# Analyze specific commit
ai-code-analyzer analyze --commit abc123

# Analyze pull request
ai-code-analyzer analyze --pr 123

# Custom output file
ai-code-analyzer analyze --commit HEAD --output my-results.json

# Verbose output
ai-code-analyzer analyze --commit HEAD --verbose
```

### Configuration Management

```bash
# Initialize configuration
ai-code-analyzer init

# Validate configuration
ai-code-analyzer validate

# Validate specific config file
ai-code-analyzer validate --config my-config.yml
```

### Version Information

```bash
# Show version
ai-code-analyzer version

# Show help
ai-code-analyzer --help
```

## 📋 Prerequisites

- Python 3.8+
- Git
- GitHub token (for GitHub integration)
- OpenAI API key or Anthropic API key (for AI features)
- Node.js 16+ (optional, for JavaScript analysis)
- Go 1.19+ (optional, for Go analysis)

## 🚀 Usage Examples

### Basic GitHub Action

```yaml
name: Code Analysis

on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: ai-code-analyzer/ai-code-analyzer@v1
      with:
        github-token: ${{ secrets.GITHUB_TOKEN }}
        openai-api-key: ${{ secrets.OPENAI_API_KEY }}
```

### Advanced GitHub Action with Load Testing

```yaml
name: Advanced Code Analysis

on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    services:
      app:
        image: my-app:latest
        ports:
          - 8000:8000
    
    steps:
    - uses: actions/checkout@v4
    - uses: ai-code-analyzer/ai-code-analyzer@v1
      with:
        github-token: ${{ secrets.GITHUB_TOKEN }}
        openai-api-key: ${{ secrets.OPENAI_API_KEY }}
        load-testing: true
        load-testing-host: http://localhost:8000
        config-file: .ai-code-analyzer.yml
```

### Python Package Usage

```python
from ai_code_analyzer import CodeAnalysisTool

# Initialize the tool
tool = CodeAnalysisTool('config.yaml')

# Analyze a commit
results = await tool.analyze_commit('abc123')

# Analyze a PR
pr_results = await tool.analyze_pr(123)
```

### CLI Usage

```bash
# Initialize configuration
ai-code-analyzer init --template advanced

# Analyze current commit
ai-code-analyzer analyze --commit HEAD

# Analyze with custom config
ai-code-analyzer analyze --commit HEAD --config my-config.yml

# Validate configuration
ai-code-analyzer validate
```

## 📁 Configuration Examples

### Basic Configuration

```yaml
# .ai-code-analyzer.yml
repository:
  path: "."

github:
  token: "${GITHUB_TOKEN}"
  owner: "${GITHUB_REPOSITORY_OWNER}"
  repo: "${GITHUB_REPOSITORY_NAME}"

ai:
  openai_api_key: "${OPENAI_API_KEY}"

risk_assessment:
  thresholds:
    low: 0
    medium: 40
    high: 60
    critical: 80
```

### Advanced Configuration

```yaml
# .ai-code-analyzer.yml
repository:
  path: "."

github:
  token: "${GITHUB_TOKEN}"
  owner: "${GITHUB_REPOSITORY_OWNER}"
  repo: "${GITHUB_REPOSITORY_NAME}"

ai:
  openai_api_key: "${OPENAI_API_KEY}"
  anthropic_api_key: "${ANTHROPIC_API_KEY}"

load_testing:
  enabled: true
  host: "http://localhost:8000"
  basic:
    users: 10
    duration: 60

analysis:
  languages:
    - python
    - javascript
    - java
    - go
  
  security:
    enable_bandit: true
    enable_safety: true
    enable_semgrep: true

testing:
  frameworks:
    python: ["pytest"]
    javascript: ["jest"]
  
  coverage:
    min_coverage: 80

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
```

## 🔍 Example Workflows

### Workflow 1: Basic PR Analysis

```bash
# .github/workflows/pr-analysis.yml
name: PR Analysis

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: ai-code-analyzer/ai-code-analyzer@v1
      with:
        github-token: ${{ secrets.GITHUB_TOKEN }}
        openai-api-key: ${{ secrets.OPENAI_API_KEY }}
        fail-on-high-risk: true
```

### Workflow 2: Release Analysis

```yaml
# .github/workflows/release-analysis.yml
name: Release Analysis

on:
  push:
    branches: [main]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: ai-code-analyzer/ai-code-analyzer@v1
      with:
        github-token: ${{ secrets.GITHUB_TOKEN }}
        openai-api-key: ${{ secrets.OPENAI_API_KEY }}
        load-testing: true
        fail-on-high-risk: false
    
    - name: Create Release Notes
      if: success()
      run: |
        # Use the generated release notes for creating releases
        echo "Release notes generated in analysis results"
```

## 📊 Output Examples

### Risk Assessment Output

```json
{
  "risk_assessment": {
    "risk_level": "medium",
    "risk_score": 45.7,
    "confidence": 0.85,
    "recommendations": [
      "Address security vulnerabilities immediately",
      "Increase test coverage to at least 80%",
      "Optimize performance bottlenecks"
    ]
  },
  "analysis": {
    "quality_score": 78.5,
    "security_issues": 2,
    "performance_issues": 1
  },
  "tests": {
    "summary": {
      "total_tests": 150,
      "passed_tests": 145,
      "coverage_percentage": 82.3
    }
  }
}
```

### CLI Output

```
🎯 Risk Assessment
┌─────────────────────────────────────┐
│ Risk Level: MEDIUM                  │
│ Risk Score: 45.7/100               │
│ Confidence: 0.85                   │
└─────────────────────────────────────┘

📊 Analysis Metrics
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric              ┃ Value               ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ Code Quality Score  │ 78.5/100           │
│ Security Issues     │ 2                   │
│ Performance Issues  │ 1                   │
│ Test Coverage       │ 82.3%              │
│ Tests Passed        │ 145/150            │
└─────────────────────┴─────────────────────┘

💡 Top Recommendations:
  1. Address security vulnerabilities immediately
  2. Increase test coverage to at least 80%
  3. Optimize performance bottlenecks
```

## 🔧 Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/ai-code-analyzer/ai-code-analyzer.git
cd ai-code-analyzer

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Run linting
black src/ tests/
isort src/ tests/
flake8 src/ tests/
```

### Building the Package

```bash
# Build the package
python -m build

# Check the package
twine check dist/*

# Upload to Test PyPI
twine upload --repository testpypi dist/*
```

## 📚 API Reference

### CodeAnalysisTool

```python
from ai_code_analyzer import CodeAnalysisTool

tool = CodeAnalysisTool(config_path="config.yaml")

# Analyze a commit
results = await tool.analyze_commit("abc123")

# Analyze a PR
pr_results = await tool.analyze_pr(123)
```

### Configuration

```python
from ai_code_analyzer import Config

config = Config("config.yaml")
value = config.get("github.token")
config.set("load_testing.enabled", True)
```

## 📊 Analysis Results

### Risk Assessment Levels

- **🟢 LOW (0-39)**: Safe to merge, minimal risk
- **🟡 MEDIUM (40-59)**: Proceed with caution, additional review recommended
- **🟠 HIGH (60-79)**: Requires thorough review, consider additional testing
- **🔴 CRITICAL (80-100)**: DO NOT MERGE, critical issues must be resolved

### Output Format

The tool generates comprehensive results in JSON format:

```json
{
  "commit_hash": "abc123",
  "risk_assessment": {
    "risk_level": "medium",
    "risk_score": 45.7,
    "confidence": 0.85,
    "recommendations": [
      "Address security vulnerabilities immediately",
      "Increase test coverage to at least 80%"
    ]
  },
  "analysis": {
    "quality_score": 78.5,
    "security_issues": ["Potential SQL injection in auth.py"],
    "performance_issues": ["Inefficient database query in search.py"]
  },
  "tests": {
    "summary": {
      "total_tests": 150,
      "passed_tests": 145,
      "failed_tests": 5,
      "coverage_percentage": 82.3
    }
  },
  "release_notes": "# Release Notes\n\n## Features\n- Added user authentication..."
}
```

## 🎯 Supported Test Frameworks

### Python
- pytest
- unittest
- nose2

### JavaScript/TypeScript
- Jest
- Mocha
- Cypress
- Playwright

### Java
- JUnit
- TestNG
- Maven
- Gradle

### Go
- go test

### Rust
- cargo test

## 🔍 Security Analysis

### Static Analysis Tools
- **Bandit**: Python security linter
- **Safety**: Python dependency vulnerability scanner
- **Semgrep**: Multi-language static analysis
- **ESLint**: JavaScript/TypeScript security rules
- **Gosec**: Go security analyzer

### Security Checks
- Hardcoded secrets detection
- SQL injection patterns
- XSS vulnerability patterns
- Command injection detection
- Insecure cryptographic practices

## ⚡ Performance Testing

### Load Testing Scenarios
- **Basic Load Test**: 10 users, 60 seconds
- **Spike Test**: 50 users, 30 seconds
- **Stress Test**: 100 users, 5 minutes
- **Endurance Test**: 20 users, 30 minutes

### Performance Metrics
- Average response time
- Requests per second
- Error rate
- Resource utilization

## 🤖 AI Integration

### OpenAI GPT-4
- Advanced code analysis
- Risk assessment
- Recommendation generation
- Release notes creation

### Anthropic Claude
- Alternative AI provider
- Advanced reasoning capabilities
- Code understanding

## 🔧 Customization

### Custom Risk Rules

Add custom rules to `config.yaml`:

```yaml
risk_assessment:
  custom_rules:
    - pattern: "eval\\s*\\("
      severity: "critical"
      message: "Use of eval() is dangerous"
    - pattern: "TODO|FIXME"
      severity: "medium"
      message: "Unresolved TODO items"
```

### Custom Test Commands

```yaml
testing:
  custom_commands:
    python: ["python -m pytest --cov=src"]
    javascript: ["npm test", "npm run test:integration"]
```

## 📚 API Documentation

### Core Classes

#### `CodeAnalyzer`
Performs static code analysis and quality checks.

#### `TestExecutor`
Executes tests and collects results.

#### `LoadTester`
Performs load testing using Locust and Artillery.

#### `AIRiskAssessment`
AI-powered risk assessment using OpenAI or Anthropic.

#### `ReleaseNotesGenerator`
Generates comprehensive release notes.

#### `GitHubIntegration`
Handles GitHub API integration.

## 🚨 Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure GitHub token has required permissions
2. **API Rate Limits**: Implement rate limiting for AI API calls
3. **Memory Issues**: Increase memory limits for large repositories
4. **Network Timeouts**: Configure appropriate timeouts for external calls

### Debug Mode

Enable debug logging:

```bash
python src/main.py --verbose --commit HEAD
```

## 🤝 Contributing to the Package

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Guidelines

```bash
# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
```

## 📦 Publishing

The package is automatically published to PyPI when a new release is created on GitHub.

### Manual Publishing

```bash
# Build the package
python -m build

# Upload to PyPI
twine upload dist/*
```

## 🔗 Links

- **PyPI Package**: https://pypi.org/project/ai-code-analyzer/
- **GitHub Repository**: https://github.com/ai-code-analyzer/ai-code-analyzer
- **Documentation**: https://ai-code-analyzer.readthedocs.io/
- **GitHub Action**: https://github.com/marketplace/actions/ai-code-analyzer
- **Issue Tracker**: https://github.com/ai-code-analyzer/ai-code-analyzer/issues

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT-4 API
- **Anthropic** for Claude API  
- **GitHub** for Actions and API
- **All open-source security and testing tools**
- **Python packaging community**

## 📞 Support

For support and questions:

1. Check the [Documentation](https://ai-code-analyzer.readthedocs.io/)
2. Search existing [Issues](https://github.com/ai-code-analyzer/ai-code-analyzer/issues)
3. Create a new issue with detailed information
4. Join our [Discord Community](https://discord.gg/ai-code-analyzer)

---

**Made with ❤️ by the AI Code Analysis Team**

[![PyPI](https://img.shields.io/pypi/v/ai-code-analyzer.svg)](https://pypi.org/project/ai-code-analyzer/)
[![Downloads](https://pepy.tech/badge/ai-code-analyzer)](https://pepy.tech/project/ai-code-analyzer)
[![GitHub stars](https://img.shields.io/github/stars/ai-code-analyzer/ai-code-analyzer.svg)](https://github.com/ai-code-analyzer/ai-code-analyzer/stargazers)