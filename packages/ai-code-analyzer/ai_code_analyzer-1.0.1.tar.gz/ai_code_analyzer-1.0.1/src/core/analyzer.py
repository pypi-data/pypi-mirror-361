"""
Code analyzer module for static analysis, security checks, and quality metrics
"""

import os
import subprocess
import ast
import json
from typing import Dict, List, Any
from pathlib import Path
import git

from utils.logger import setup_logger

logger = setup_logger(__name__)


class CodeAnalyzer:
    """Performs comprehensive code analysis"""
    
    def __init__(self, config):
        self.config = config
        self.repo_path = config.get("repository.path", ".")
        self.supported_languages = {
            'python': ['.py'],
            'javascript': ['.js', '.jsx', '.ts', '.tsx'],
            'java': ['.java'],
            'go': ['.go'],
            'rust': ['.rs'],
            'c': ['.c', '.h'],
            'cpp': ['.cpp', '.cc', '.cxx', '.hpp'],
            'ruby': ['.rb'],
            'php': ['.php'],
            'swift': ['.swift'],
            'kotlin': ['.kt'],
            'scala': ['.scala']
        }
    
    async def analyze_commit(self, commit_hash: str) -> Dict:
        """Analyze a specific commit"""
        logger.info(f"Analyzing commit: {commit_hash}")
        
        try:
            repo = git.Repo(self.repo_path)
            commit = repo.commit(commit_hash)
            
            # Get changed files
            changed_files = self._get_changed_files(commit)
            
            analysis_result = {
                "commit_hash": commit_hash,
                "author": commit.author.name,
                "message": commit.message,
                "timestamp": commit.committed_datetime.isoformat(),
                "changed_files": changed_files,
                "language_distribution": self._analyze_language_distribution(changed_files),
                "security_issues": [],
                "code_quality": {},
                "complexity_metrics": {},
                "performance_issues": [],
                "best_practices": {},
                "quality_score": 0
            }
            
            # Analyze each changed file
            for file_path in changed_files:
                if self._is_code_file(file_path):
                    file_analysis = await self._analyze_file(file_path, commit_hash)
                    self._merge_analysis_results(analysis_result, file_analysis)
            
            # Calculate overall quality score
            analysis_result["quality_score"] = self._calculate_quality_score(analysis_result)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing commit {commit_hash}: {str(e)}")
            return {"error": str(e), "commit_hash": commit_hash}
    
    def _get_changed_files(self, commit) -> List[str]:
        """Get list of files changed in the commit"""
        try:
            # Get the diff for the commit
            if commit.parents:
                diff = commit.parents[0].diff(commit)
            else:
                # First commit
                diff = commit.diff(None)
            
            changed_files = []
            for item in diff:
                if item.a_path:
                    changed_files.append(item.a_path)
                if item.b_path and item.b_path != item.a_path:
                    changed_files.append(item.b_path)
            
            return list(set(changed_files))
            
        except Exception as e:
            logger.error(f"Error getting changed files: {str(e)}")
            return []
    
    def _analyze_language_distribution(self, files: List[str]) -> Dict:
        """Analyze the distribution of programming languages"""
        language_count = {}
        
        for file_path in files:
            lang = self._detect_language(file_path)
            if lang:
                language_count[lang] = language_count.get(lang, 0) + 1
        
        return language_count
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        ext = Path(file_path).suffix.lower()
        
        for lang, extensions in self.supported_languages.items():
            if ext in extensions:
                return lang
        
        return "unknown"
    
    def _is_code_file(self, file_path: str) -> bool:
        """Check if file is a code file"""
        return self._detect_language(file_path) != "unknown"
    
    async def _analyze_file(self, file_path: str, commit_hash: str) -> Dict:
        """Analyze a single file"""
        logger.debug(f"Analyzing file: {file_path}")
        
        analysis = {
            "file_path": file_path,
            "language": self._detect_language(file_path),
            "security_issues": [],
            "complexity": {},
            "quality_issues": [],
            "performance_issues": [],
            "lines_of_code": 0,
            "cyclomatic_complexity": 0
        }
        
        try:
            full_path = os.path.join(self.repo_path, file_path)
            
            if not os.path.exists(full_path):
                return analysis
            
            # Read file content
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            analysis["lines_of_code"] = len(content.splitlines())
            
            # Language-specific analysis
            if analysis["language"] == "python":
                analysis.update(await self._analyze_python_file(content, file_path))
            elif analysis["language"] == "javascript":
                analysis.update(await self._analyze_javascript_file(content, file_path))
            elif analysis["language"] == "java":
                analysis.update(await self._analyze_java_file(content, file_path))
            elif analysis["language"] == "go":
                analysis.update(await self._analyze_go_file(content, file_path))
            
            # General security analysis
            analysis["security_issues"].extend(await self._analyze_security(content, file_path))
            
            # Performance analysis
            analysis["performance_issues"].extend(await self._analyze_performance(content, file_path))
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {str(e)}")
            analysis["error"] = str(e)
        
        return analysis
    
    async def _analyze_python_file(self, content: str, file_path: str) -> Dict:
        """Analyze Python-specific metrics"""
        analysis = {
            "complexity": {},
            "quality_issues": [],
            "security_issues": []
        }
        
        try:
            # Parse AST
            tree = ast.parse(content)
            
            # Calculate cyclomatic complexity
            complexity = self._calculate_cyclomatic_complexity_python(tree)
            analysis["cyclomatic_complexity"] = complexity
            
            # Check for common Python issues
            analysis["quality_issues"].extend(self._check_python_best_practices(tree))
            analysis["security_issues"].extend(self._check_python_security(tree))
            
            # Run additional tools
            await self._run_python_linters(file_path, analysis)
            
        except SyntaxError as e:
            analysis["quality_issues"].append(f"Syntax error: {str(e)}")
        except Exception as e:
            logger.error(f"Error analyzing Python file {file_path}: {str(e)}")
        
        return analysis
    
    async def _analyze_javascript_file(self, content: str, file_path: str) -> Dict:
        """Analyze JavaScript-specific metrics"""
        analysis = {
            "complexity": {},
            "quality_issues": [],
            "security_issues": []
        }
        
        try:
            # Run ESLint if available
            await self._run_eslint(file_path, analysis)
            
            # Check for common JavaScript security issues
            analysis["security_issues"].extend(self._check_javascript_security(content))
            
        except Exception as e:
            logger.error(f"Error analyzing JavaScript file {file_path}: {str(e)}")
        
        return analysis
    
    async def _analyze_java_file(self, content: str, file_path: str) -> Dict:
        """Analyze Java-specific metrics"""
        analysis = {
            "complexity": {},
            "quality_issues": [],
            "security_issues": []
        }
        
        try:
            # Run SpotBugs or similar if available
            await self._run_java_analyzers(file_path, analysis)
            
        except Exception as e:
            logger.error(f"Error analyzing Java file {file_path}: {str(e)}")
        
        return analysis
    
    async def _analyze_go_file(self, content: str, file_path: str) -> Dict:
        """Analyze Go-specific metrics"""
        analysis = {
            "complexity": {},
            "quality_issues": [],
            "security_issues": []
        }
        
        try:
            # Run go vet and other Go tools
            await self._run_go_analyzers(file_path, analysis)
            
        except Exception as e:
            logger.error(f"Error analyzing Go file {file_path}: {str(e)}")
        
        return analysis
    
    async def _analyze_security(self, content: str, file_path: str) -> List[str]:
        """General security analysis"""
        security_issues = []
        
        # Common security patterns
        security_patterns = [
            ("hardcoded_password", r"password\s*=\s*['\"][^'\"]+['\"]"),
            ("hardcoded_api_key", r"api_key\s*=\s*['\"][^'\"]+['\"]"),
            ("sql_injection", r"SELECT.*\+.*"),
            ("xss_vulnerability", r"innerHTML\s*=\s*.*\+"),
            ("command_injection", r"system\s*\(.*\+"),
        ]
        
        import re
        for issue_type, pattern in security_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                security_issues.append(f"Potential {issue_type} in {file_path}")
        
        return security_issues
    
    async def _analyze_performance(self, content: str, file_path: str) -> List[str]:
        """Performance analysis"""
        performance_issues = []
        
        # Common performance anti-patterns
        performance_patterns = [
            ("nested_loops", r"for.*for.*for"),
            ("inefficient_string_concat", r"\+\s*=\s*['\"]"),
            ("blocking_io", r"\.read\(\)"),
        ]
        
        import re
        for issue_type, pattern in performance_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                performance_issues.append(f"Potential {issue_type} in {file_path}")
        
        return performance_issues
    
    def _calculate_cyclomatic_complexity_python(self, tree) -> int:
        """Calculate cyclomatic complexity for Python code"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _check_python_best_practices(self, tree) -> List[str]:
        """Check Python best practices"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if len(node.args.args) > 7:
                    issues.append(f"Function '{node.name}' has too many parameters")
                
                if not node.returns and not any(isinstance(n, ast.Return) for n in ast.walk(node)):
                    issues.append(f"Function '{node.name}' has no return statement")
        
        return issues
    
    def _check_python_security(self, tree) -> List[str]:
        """Check Python security issues"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id == "eval":
                        issues.append("Use of eval() is dangerous")
                    elif node.func.id == "exec":
                        issues.append("Use of exec() is dangerous")
        
        return issues
    
    def _check_javascript_security(self, content: str) -> List[str]:
        """Check JavaScript security issues"""
        issues = []
        
        import re
        if re.search(r"eval\s*\(", content):
            issues.append("Use of eval() is dangerous")
        
        if re.search(r"document\.write\s*\(", content):
            issues.append("Use of document.write() can lead to XSS")
        
        return issues
    
    async def _run_python_linters(self, file_path: str, analysis: Dict):
        """Run Python linters"""
        try:
            # Run pylint
            result = subprocess.run(
                ["pylint", "--output-format=json", file_path],
                capture_output=True,
                text=True,
                cwd=self.repo_path
            )
            
            if result.stdout:
                pylint_results = json.loads(result.stdout)
                for issue in pylint_results:
                    analysis["quality_issues"].append(f"Pylint: {issue['message']}")
        
        except Exception as e:
            logger.debug(f"Pylint not available or failed: {str(e)}")
    
    async def _run_eslint(self, file_path: str, analysis: Dict):
        """Run ESLint"""
        try:
            result = subprocess.run(
                ["eslint", "--format", "json", file_path],
                capture_output=True,
                text=True,
                cwd=self.repo_path
            )
            
            if result.stdout:
                eslint_results = json.loads(result.stdout)
                for file_result in eslint_results:
                    for message in file_result.get("messages", []):
                        analysis["quality_issues"].append(f"ESLint: {message['message']}")
        
        except Exception as e:
            logger.debug(f"ESLint not available or failed: {str(e)}")
    
    async def _run_java_analyzers(self, file_path: str, analysis: Dict):
        """Run Java analyzers"""
        # Placeholder for Java-specific analyzers
        pass
    
    async def _run_go_analyzers(self, file_path: str, analysis: Dict):
        """Run Go analyzers"""
        try:
            # Run go vet
            result = subprocess.run(
                ["go", "vet", file_path],
                capture_output=True,
                text=True,
                cwd=self.repo_path
            )
            
            if result.stderr:
                analysis["quality_issues"].append(f"Go vet: {result.stderr}")
        
        except Exception as e:
            logger.debug(f"Go vet not available or failed: {str(e)}")
    
    def _merge_analysis_results(self, main_analysis: Dict, file_analysis: Dict):
        """Merge file analysis results into main analysis"""
        main_analysis["security_issues"].extend(file_analysis.get("security_issues", []))
        main_analysis["performance_issues"].extend(file_analysis.get("performance_issues", []))
        
        # Update complexity metrics
        if "complexity" not in main_analysis:
            main_analysis["complexity"] = {}
        
        if file_analysis.get("cyclomatic_complexity"):
            main_analysis["complexity"][file_analysis["file_path"]] = file_analysis["cyclomatic_complexity"]
    
    def _calculate_quality_score(self, analysis: Dict) -> float:
        """Calculate overall quality score (0-100)"""
        score = 100.0
        
        # Deduct points for issues
        score -= len(analysis.get("security_issues", [])) * 10
        score -= len(analysis.get("performance_issues", [])) * 5
        
        # Adjust for complexity
        avg_complexity = 0
        if analysis.get("complexity"):
            avg_complexity = sum(analysis["complexity"].values()) / len(analysis["complexity"])
        
        if avg_complexity > 10:
            score -= (avg_complexity - 10) * 2
        
        return max(0, min(100, score))