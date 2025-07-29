"""
Release notes generator module
"""

import json
import re
from typing import Dict, List, Any
from datetime import datetime

from utils.logger import setup_logger

logger = setup_logger(__name__)


class ReleaseNotesGenerator:
    """Generates comprehensive release notes from analysis results"""
    
    def __init__(self, config):
        self.config = config
        self.commit_categories = {
            "feat": "🚀 Features",
            "fix": "🐛 Bug Fixes",
            "docs": "📚 Documentation",
            "style": "💅 Style Changes",
            "refactor": "♻️ Code Refactoring",
            "perf": "⚡ Performance Improvements",
            "test": "🧪 Testing",
            "build": "🔧 Build System",
            "ci": "👷 CI/CD",
            "chore": "🔨 Maintenance",
            "security": "🔒 Security",
            "breaking": "💥 Breaking Changes"
        }
    
    async def generate(self, analysis_results: Dict) -> str:
        """Generate comprehensive release notes"""
        logger.info("Generating release notes")
        
        try:
            # Extract commit information
            commit_info = self._extract_commit_info(analysis_results)
            
            # Categorize changes
            categorized_changes = self._categorize_changes(commit_info)
            
            # Generate quality metrics
            quality_metrics = self._generate_quality_metrics(analysis_results)
            
            # Generate test summary
            test_summary = self._generate_test_summary(analysis_results)
            
            # Generate performance summary
            performance_summary = self._generate_performance_summary(analysis_results)
            
            # Generate security summary
            security_summary = self._generate_security_summary(analysis_results)
            
            # Generate risk assessment summary
            risk_summary = self._generate_risk_summary(analysis_results)
            
            # Compile release notes
            release_notes = self._compile_release_notes(
                commit_info,
                categorized_changes,
                quality_metrics,
                test_summary,
                performance_summary,
                security_summary,
                risk_summary
            )
            
            logger.info("Release notes generated successfully")
            return release_notes
            
        except Exception as e:
            logger.error(f"Error generating release notes: {str(e)}")
            return f"Error generating release notes: {str(e)}"
    
    def _extract_commit_info(self, analysis_results: Dict) -> Dict:
        """Extract commit information from analysis results"""
        commit_info = {
            "hash": analysis_results.get("commit_hash", "unknown"),
            "author": analysis_results.get("analysis", {}).get("author", "unknown"),
            "message": analysis_results.get("analysis", {}).get("message", ""),
            "timestamp": analysis_results.get("analysis", {}).get("timestamp", ""),
            "changed_files": analysis_results.get("analysis", {}).get("changed_files", [])
        }
        
        return commit_info
    
    def _categorize_changes(self, commit_info: Dict) -> Dict:
        """Categorize changes based on commit message and files"""
        categorized = {category: [] for category in self.commit_categories.values()}
        categorized["uncategorized"] = []
        
        message = commit_info.get("message", "").lower()
        changed_files = commit_info.get("changed_files", [])
        
        # Analyze commit message for conventional commit format
        category = self._detect_commit_category(message)
        
        # Extract the actual change description
        change_description = self._extract_change_description(commit_info.get("message", ""))
        
        # Add file-based categorization
        file_categories = self._categorize_by_files(changed_files)
        
        change_entry = {
            "description": change_description,
            "files": changed_files,
            "commit": commit_info.get("hash", "")[:8],
            "author": commit_info.get("author", ""),
            "timestamp": commit_info.get("timestamp", "")
        }
        
        if category:
            categorized[self.commit_categories[category]].append(change_entry)
        else:
            # Use file-based categorization as fallback
            if file_categories:
                for file_category in file_categories:
                    if file_category in self.commit_categories:
                        categorized[self.commit_categories[file_category]].append(change_entry)
                        break
                else:
                    categorized["uncategorized"].append(change_entry)
            else:
                categorized["uncategorized"].append(change_entry)
        
        return categorized
    
    def _detect_commit_category(self, message: str) -> str:
        """Detect commit category from message"""
        # Conventional commit format: type(scope): description
        conventional_pattern = r'^(feat|fix|docs|style|refactor|perf|test|build|ci|chore)(\(.+\))?: .+'
        
        match = re.match(conventional_pattern, message)
        if match:
            return match.group(1)
        
        # Keyword-based detection
        if any(keyword in message for keyword in ["security", "vulnerability", "exploit", "cve"]):
            return "security"
        
        if any(keyword in message for keyword in ["breaking", "breaking change", "major"]):
            return "breaking"
        
        if any(keyword in message for keyword in ["fix", "bug", "issue", "error", "crash"]):
            return "fix"
        
        if any(keyword in message for keyword in ["feature", "add", "new", "implement"]):
            return "feat"
        
        if any(keyword in message for keyword in ["performance", "optimize", "speed", "memory"]):
            return "perf"
        
        if any(keyword in message for keyword in ["test", "testing", "spec", "coverage"]):
            return "test"
        
        if any(keyword in message for keyword in ["doc", "documentation", "readme"]):
            return "docs"
        
        if any(keyword in message for keyword in ["refactor", "restructure", "reorganize"]):
            return "refactor"
        
        if any(keyword in message for keyword in ["style", "format", "lint", "prettier"]):
            return "style"
        
        if any(keyword in message for keyword in ["build", "webpack", "rollup", "compile"]):
            return "build"
        
        if any(keyword in message for keyword in ["ci", "cd", "pipeline", "github actions", "travis"]):
            return "ci"
        
        return None
    
    def _categorize_by_files(self, changed_files: List[str]) -> List[str]:
        """Categorize changes by file types"""
        categories = []
        
        for file_path in changed_files:
            file_lower = file_path.lower()
            
            # Test files
            if any(pattern in file_lower for pattern in ["test", "spec", "__test__", ".test.", ".spec."]):
                categories.append("test")
            
            # Documentation files
            elif any(pattern in file_lower for pattern in ["readme", "doc", ".md", "changelog", "license"]):
                categories.append("docs")
            
            # Build/CI files
            elif any(pattern in file_lower for pattern in [
                "dockerfile", "docker-compose", "makefile", "webpack", "rollup", "vite.config",
                "package.json", "requirements.txt", "cargo.toml", "pom.xml", "build.gradle",
                ".github", "ci", "cd", "pipeline", ".yml", ".yaml"
            ]):
                categories.append("build")
            
            # Configuration files
            elif any(pattern in file_lower for pattern in [
                "config", "settings", ".env", ".ini", ".conf", ".cfg"
            ]):
                categories.append("chore")
            
            # Style files
            elif any(pattern in file_lower for pattern in [".css", ".scss", ".sass", ".less", ".styl"]):
                categories.append("style")
        
        return categories
    
    def _extract_change_description(self, commit_message: str) -> str:
        """Extract clean change description from commit message"""
        # Remove conventional commit prefix
        conventional_pattern = r'^(feat|fix|docs|style|refactor|perf|test|build|ci|chore)(\(.+\))?: '
        cleaned = re.sub(conventional_pattern, '', commit_message)
        
        # Take first line only
        first_line = cleaned.split('\n')[0].strip()
        
        # Capitalize first letter
        if first_line:
            first_line = first_line[0].upper() + first_line[1:]
        
        return first_line or commit_message
    
    def _generate_quality_metrics(self, analysis_results: Dict) -> Dict:
        """Generate quality metrics summary"""
        analysis = analysis_results.get("analysis", {})
        
        metrics = {
            "code_quality_score": analysis.get("quality_score", 0),
            "security_issues": len(analysis.get("security_issues", [])),
            "performance_issues": len(analysis.get("performance_issues", [])),
            "complexity_score": self._calculate_complexity_score(analysis.get("complexity_metrics", {})),
            "files_changed": len(analysis.get("changed_files", [])),
            "lines_of_code": analysis.get("lines_of_code", 0)
        }
        
        return metrics
    
    def _calculate_complexity_score(self, complexity_metrics: Dict) -> float:
        """Calculate average complexity score"""
        if not complexity_metrics:
            return 0
        
        return sum(complexity_metrics.values()) / len(complexity_metrics)
    
    def _generate_test_summary(self, analysis_results: Dict) -> Dict:
        """Generate test summary"""
        tests = analysis_results.get("tests", {})
        summary = tests.get("summary", {})
        
        return {
            "total_tests": summary.get("total_tests", 0),
            "passed_tests": summary.get("passed_tests", 0),
            "failed_tests": summary.get("failed_tests", 0),
            "skipped_tests": summary.get("skipped_tests", 0),
            "coverage_percentage": summary.get("coverage_percentage", 0),
            "test_status": tests.get("overall_status", "unknown")
        }
    
    def _generate_performance_summary(self, analysis_results: Dict) -> Dict:
        """Generate performance summary"""
        load_testing = analysis_results.get("load_testing", {})
        
        if not load_testing or load_testing.get("status") == "skipped":
            return {"status": "not_tested"}
        
        summary = load_testing.get("summary", {})
        
        return {
            "status": "tested",
            "performance_grade": summary.get("performance_grade", "unknown"),
            "average_response_time": summary.get("overall_avg_response_time", 0),
            "requests_per_second": summary.get("overall_rps", 0),
            "failure_rate": summary.get("overall_failure_rate", 0)
        }
    
    def _generate_security_summary(self, analysis_results: Dict) -> Dict:
        """Generate security summary"""
        analysis = analysis_results.get("analysis", {})
        tests = analysis_results.get("tests", {})
        
        security_issues = analysis.get("security_issues", [])
        security_tests = tests.get("security_tests", {})
        
        return {
            "static_analysis_issues": len(security_issues),
            "security_scan_results": {
                "bandit": security_tests.get("bandit", {}).get("issues_found", 0),
                "safety": security_tests.get("safety", {}).get("vulnerabilities_found", 0),
                "semgrep": security_tests.get("semgrep", {}).get("findings", 0)
            },
            "overall_security_status": "secure" if len(security_issues) == 0 else "issues_found"
        }
    
    def _generate_risk_summary(self, analysis_results: Dict) -> Dict:
        """Generate risk assessment summary"""
        risk_assessment = analysis_results.get("risk_assessment", {})
        
        return {
            "risk_level": risk_assessment.get("risk_level", "unknown"),
            "risk_score": risk_assessment.get("risk_score", 0),
            "confidence": risk_assessment.get("confidence", 0),
            "key_risk_factors": list(risk_assessment.get("risk_factors", {}).keys())
        }
    
    def _compile_release_notes(self, commit_info: Dict, categorized_changes: Dict, 
                             quality_metrics: Dict, test_summary: Dict, 
                             performance_summary: Dict, security_summary: Dict, 
                             risk_summary: Dict) -> str:
        """Compile all information into formatted release notes"""
        
        release_notes = []
        
        # Header
        release_notes.append("# 🚀 Release Notes")
        release_notes.append("")
        release_notes.append(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        release_notes.append(f"**Commit:** `{commit_info.get('hash', 'unknown')}`")
        release_notes.append(f"**Author:** {commit_info.get('author', 'unknown')}")
        release_notes.append("")
        
        # Risk Assessment
        risk_level = risk_summary.get("risk_level", "unknown")
        risk_emoji = {
            "low": "✅",
            "medium": "⚠️",
            "high": "🚨",
            "critical": "❌"
        }.get(risk_level, "❓")
        
        release_notes.append("## 🎯 Risk Assessment")
        release_notes.append("")
        release_notes.append(f"**Overall Risk Level:** {risk_emoji} {risk_level.upper()}")
        release_notes.append(f"**Risk Score:** {risk_summary.get('risk_score', 0):.1f}/100")
        release_notes.append(f"**Confidence:** {risk_summary.get('confidence', 0):.1f}")
        release_notes.append("")
        
        # Changes
        release_notes.append("## 📋 Changes")
        release_notes.append("")
        
        for category, changes in categorized_changes.items():
            if changes and category != "uncategorized":
                release_notes.append(f"### {category}")
                release_notes.append("")
                for change in changes:
                    release_notes.append(f"- {change['description']} ({change['commit']})")
                release_notes.append("")
        
        # Uncategorized changes
        if categorized_changes.get("uncategorized"):
            release_notes.append("### 📝 Other Changes")
            release_notes.append("")
            for change in categorized_changes["uncategorized"]:
                release_notes.append(f"- {change['description']} ({change['commit']})")
            release_notes.append("")
        
        # Quality Metrics
        release_notes.append("## 📊 Quality Metrics")
        release_notes.append("")
        release_notes.append(f"- **Code Quality Score:** {quality_metrics.get('code_quality_score', 0):.1f}/100")
        release_notes.append(f"- **Files Changed:** {quality_metrics.get('files_changed', 0)}")
        release_notes.append(f"- **Lines of Code:** {quality_metrics.get('lines_of_code', 0)}")
        release_notes.append(f"- **Average Complexity:** {quality_metrics.get('complexity_score', 0):.1f}")
        release_notes.append(f"- **Security Issues:** {quality_metrics.get('security_issues', 0)}")
        release_notes.append(f"- **Performance Issues:** {quality_metrics.get('performance_issues', 0)}")
        release_notes.append("")
        
        # Test Results
        release_notes.append("## 🧪 Test Results")
        release_notes.append("")
        
        test_status = test_summary.get("test_status", "unknown")
        test_emoji = "✅" if test_status == "passed" else "❌" if test_status == "failed" else "❓"
        
        release_notes.append(f"**Overall Status:** {test_emoji} {test_status.upper()}")
        release_notes.append("")
        release_notes.append(f"- **Total Tests:** {test_summary.get('total_tests', 0)}")
        release_notes.append(f"- **Passed:** {test_summary.get('passed_tests', 0)}")
        release_notes.append(f"- **Failed:** {test_summary.get('failed_tests', 0)}")
        release_notes.append(f"- **Skipped:** {test_summary.get('skipped_tests', 0)}")
        release_notes.append(f"- **Coverage:** {test_summary.get('coverage_percentage', 0):.1f}%")
        release_notes.append("")
        
        # Performance Results
        if performance_summary.get("status") == "tested":
            release_notes.append("## ⚡ Performance Results")
            release_notes.append("")
            
            grade = performance_summary.get("performance_grade", "unknown")
            grade_emoji = {
                "A": "🌟",
                "B": "✅",
                "C": "⚠️",
                "D": "🚨",
                "F": "❌"
            }.get(grade, "❓")
            
            release_notes.append(f"**Performance Grade:** {grade_emoji} {grade}")
            release_notes.append("")
            release_notes.append(f"- **Average Response Time:** {performance_summary.get('average_response_time', 0):.0f}ms")
            release_notes.append(f"- **Requests per Second:** {performance_summary.get('requests_per_second', 0):.1f}")
            release_notes.append(f"- **Failure Rate:** {performance_summary.get('failure_rate', 0):.2f}%")
            release_notes.append("")
        
        # Security Results
        release_notes.append("## 🔒 Security Analysis")
        release_notes.append("")
        
        security_status = security_summary.get("overall_security_status", "unknown")
        security_emoji = "✅" if security_status == "secure" else "🚨"
        
        release_notes.append(f"**Overall Security Status:** {security_emoji} {security_status.upper()}")
        release_notes.append("")
        release_notes.append(f"- **Static Analysis Issues:** {security_summary.get('static_analysis_issues', 0)}")
        
        scan_results = security_summary.get("security_scan_results", {})
        if scan_results:
            release_notes.append("- **Security Scan Results:**")
            if scan_results.get("bandit", 0) > 0:
                release_notes.append(f"  - Bandit: {scan_results['bandit']} issues")
            if scan_results.get("safety", 0) > 0:
                release_notes.append(f"  - Safety: {scan_results['safety']} vulnerabilities")
            if scan_results.get("semgrep", 0) > 0:
                release_notes.append(f"  - Semgrep: {scan_results['semgrep']} findings")
        
        release_notes.append("")
        
        # Recommendations
        risk_assessment = analysis_results.get("risk_assessment", {})
        recommendations = risk_assessment.get("recommendations", [])
        
        if recommendations:
            release_notes.append("## 💡 Recommendations")
            release_notes.append("")
            for recommendation in recommendations:
                release_notes.append(f"- {recommendation}")
            release_notes.append("")
        
        # Footer
        release_notes.append("---")
        release_notes.append("")
        release_notes.append("*Generated by AI-Powered Code Analysis Tool*")
        
        return "\n".join(release_notes)