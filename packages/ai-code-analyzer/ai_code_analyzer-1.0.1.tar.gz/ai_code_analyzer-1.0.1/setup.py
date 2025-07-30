#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read README.md
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements.txt
with open(os.path.join(this_directory, 'requirements.txt')) as f:
    requirements = f.read().splitlines()

setup(
    name="ai-code-analyzer",
    version="1.0.2",  # ⬅️ Incremented version for update
    author="AI Code Analysis Team",
    author_email="team@ai-code-analyzer.com",
    description="AI-powered code analysis tool for CI/CD pipelines with GitHub Actions integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ai-code-analyzer/ai-code-analyzer",
    packages=find_packages(where="src", include=['ai_code_analyzer', 'ai_code_analyzer.*']),# ⬅️ Includes src/ai_code_analyzer/core/*
    package_dir={"": "src"},                   # ⬅️ Maps root to src/
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ai-code-analyzer=cli:main",
            "aca=cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "ai_code_analyzer": [
            "templates/*.yaml",
            "templates/*.yml",
            "config/*.yaml",
            "config/*.yml",
        ],
    },
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "all": [
            "pylint>=3.0.0",
            "bandit>=1.7.0",
            "safety>=2.0.0",
            "semgrep>=1.0.0",
            "locust>=2.0.0",
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="ai code-analysis ci-cd github-actions testing security performance",
    project_urls={
        "Bug Reports": "https://github.com/ai-code-analyzer/ai-code-analyzer/issues",
        "Source": "https://github.com/ai-code-analyzer/ai-code-analyzer",
        "Documentation": "https://ai-code-analyzer.readthedocs.io/",
    },
)
