"""
GitHub integration module for CI/CD pipeline
"""

import asyncio
import json
import os
from typing import Dict, List, Optional
import aiohttp

from utils.logger import setup_logger

logger = setup_logger(__name__)


class GitHubIntegration:
    """Handles GitHub API integration for PR status updates"""
    
    def __init__(self, config):
        self.config = config
        self.github_token = config.get("github.token") or os.getenv("GITHUB_TOKEN")
        self.repo_owner = config.get("github.owner") or os.getenv("GITHUB_REPOSITORY_OWNER")
        self.repo_name = config.get("github.repo") or os.getenv("GITHUB_REPOSITORY_NAME")
        self.api_base_url = "https://api.github.com"
        
        if not self.github_token:
            logger.warning("GitHub token not found. GitHub integration will be disabled.")
    
    async def get_pr_info(self, pr_number: int) -> Dict:
        """Get PR information from GitHub API"""
        if not self._is_configured():
            return {}
        
        try:
            url = f"{self.api_base_url}/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self._get_headers()) as response:
                    if response.status == 200:
                        pr_data = await response.json()
                        
                        # Get commits for the PR
                        commits = await self._get_pr_commits(pr_number)
                        
                        return {
                            "number": pr_data["number"],
                            "title": pr_data["title"],
                            "body": pr_data.get("body", ""),
                            "state": pr_data["state"],
                            "author": pr_data["user"]["login"],
                            "created_at": pr_data["created_at"],
                            "updated_at": pr_data["updated_at"],
                            "head_sha": pr_data["head"]["sha"],
                            "base_branch": pr_data["base"]["ref"],
                            "head_branch": pr_data["head"]["ref"],
                            "commits": commits
                        }
                    else:
                        logger.error(f"Failed to get PR info: {response.status}")
                        return {}
        
        except Exception as e:
            logger.error(f"Error getting PR info: {str(e)}")
            return {}
    
    async def _get_pr_commits(self, pr_number: int) -> List[Dict]:
        """Get commits for a PR"""
        try:
            url = f"{self.api_base_url}/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}/commits"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self._get_headers()) as response:
                    if response.status == 200:
                        commits_data = await response.json()
                        
                        return [
                            {
                                "sha": commit["sha"],
                                "message": commit["commit"]["message"],
                                "author": commit["commit"]["author"]["name"],
                                "date": commit["commit"]["author"]["date"]
                            }
                            for commit in commits_data
                        ]
                    else:
                        logger.error(f"Failed to get PR commits: {response.status}")
                        return []
        
        except Exception as e:
            logger.error(f"Error getting PR commits: {str(e)}")
            return []
    
    async def update_pr_status(self, pr_number: int, analysis_results: Dict):
        """Update PR with analysis results"""
        if not self._is_configured():
            logger.warning("GitHub not configured, skipping PR update")
            return
        
        try:
            # Create check run
            await self._create_check_run(analysis_results)
            
            # Add comment to PR
            await self._add_pr_comment(pr_number, analysis_results)
            
            # Update PR status
            await self._update_pr_status_check(analysis_results)
            
        except Exception as e:
            logger.error(f"Error updating PR status: {str(e)}")
    
    async def _create_check_run(self, analysis_results: Dict):
        """Create a check run for the commit"""
        try:
            commit_sha = analysis_results.get("commit_hash")
            if not commit_sha:
                return
            
            risk_assessment = analysis_results.get("risk_assessment", {})
            risk_level = risk_assessment.get("risk_level", "unknown")
            
            # Determine check run status
            conclusion = self._get_check_conclusion(risk_level)
            status = "completed"
            
            # Create check run payload
            check_run_data = {
                "name": "AI Code Analysis",
                "head_sha": commit_sha,
                "status": status,
                "conclusion": conclusion,
                "output": {
                    "title": f"Code Analysis - Risk Level: {risk_level.upper()}",
                    "summary": self._generate_check_summary(analysis_results),
                    "text": self._generate_check_details(analysis_results)
                }
            }
            
            url = f"{self.api_base_url}/repos/{self.repo_owner}/{self.repo_name}/check-runs"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self._get_headers(), json=check_run_data) as response:
                    if response.status == 201:
                        logger.info("Check run created successfully")
                    else:
                        logger.error(f"Failed to create check run: {response.status}")
                        response_text = await response.text()
                        logger.error(f"Response: {response_text}")
        
        except Exception as e:
            logger.error(f"Error creating check run: {str(e)}")
    
    def _get_check_conclusion(self, risk_level: str) -> str:
        """Get check run conclusion based on risk level"""
        if risk_level == "low":
            return "success"
        elif risk_level == "medium":
            return "neutral"
        elif risk_level == "high":
            return "failure"
        elif risk_level == "critical":
            return "failure"
        else:
            return "neutral"
    
    def _generate_check_summary(self, analysis_results: Dict) -> str:
        """Generate check run summary"""
        risk_assessment = analysis_results.get("risk_assessment", {})
        risk_level = risk_assessment.get("risk_level", "unknown")
        risk_score = risk_assessment.get("risk_score", 0)
        
        # Test results
        tests = analysis_results.get("tests", {})
        test_summary = tests.get("summary", {})
        
        # Quality metrics
        analysis = analysis_results.get("analysis", {})
        quality_score = analysis.get("quality_score", 0)
        
        summary = f"""
**Risk Assessment:** {risk_level.upper()} (Score: {risk_score:.1f}/100)
**Code Quality:** {quality_score:.1f}/100
**Test Results:** {test_summary.get('passed_tests', 0)}/{test_summary.get('total_tests', 0)} passed
**Coverage:** {test_summary.get('coverage_percentage', 0):.1f}%
**Security Issues:** {len(analysis.get('security_issues', []))}
"""
        
        return summary.strip()
    
    def _generate_check_details(self, analysis_results: Dict) -> str:
        """Generate detailed check run output"""
        details = []
        
        # Risk assessment details
        risk_assessment = analysis_results.get("risk_assessment", {})
        details.append("## Risk Assessment")
        details.append("")
        details.append(f"**Risk Level:** {risk_assessment.get('risk_level', 'unknown').upper()}")
        details.append(f"**Risk Score:** {risk_assessment.get('risk_score', 0):.1f}/100")
        details.append(f"**Confidence:** {risk_assessment.get('confidence', 0):.1f}")
        details.append("")
        
        # Recommendations
        recommendations = risk_assessment.get("recommendations", [])
        if recommendations:
            details.append("## Recommendations")
            details.append("")
            for rec in recommendations[:5]:  # Limit to top 5
                details.append(f"- {rec}")
            details.append("")
        
        # Code quality issues
        analysis = analysis_results.get("analysis", {})
        security_issues = analysis.get("security_issues", [])
        performance_issues = analysis.get("performance_issues", [])
        
        if security_issues:
            details.append("## Security Issues")
            details.append("")
            for issue in security_issues[:3]:  # Limit to top 3
                details.append(f"- {issue}")
            details.append("")
        
        if performance_issues:
            details.append("## Performance Issues")
            details.append("")
            for issue in performance_issues[:3]:  # Limit to top 3
                details.append(f"- {issue}")
            details.append("")
        
        # Test results
        tests = analysis_results.get("tests", {})
        test_summary = tests.get("summary", {})
        
        details.append("## Test Results")
        details.append("")
        details.append(f"- **Total Tests:** {test_summary.get('total_tests', 0)}")
        details.append(f"- **Passed:** {test_summary.get('passed_tests', 0)}")
        details.append(f"- **Failed:** {test_summary.get('failed_tests', 0)}")
        details.append(f"- **Coverage:** {test_summary.get('coverage_percentage', 0):.1f}%")
        details.append("")
        
        return "\n".join(details)
    
    async def _add_pr_comment(self, pr_number: int, analysis_results: Dict):
        """Add comment to PR with analysis results"""
        try:
            # Generate comment content
            comment_body = self._generate_pr_comment(analysis_results)
            
            # Check if we already have a comment
            existing_comment_id = await self._find_existing_comment(pr_number)
            
            if existing_comment_id:
                # Update existing comment
                await self._update_pr_comment(existing_comment_id, comment_body)
            else:
                # Create new comment
                await self._create_pr_comment(pr_number, comment_body)
        
        except Exception as e:
            logger.error(f"Error adding PR comment: {str(e)}")
    
    async def _find_existing_comment(self, pr_number: int) -> Optional[int]:
        """Find existing bot comment on PR"""
        try:
            url = f"{self.api_base_url}/repos/{self.repo_owner}/{self.repo_name}/issues/{pr_number}/comments"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self._get_headers()) as response:
                    if response.status == 200:
                        comments = await response.json()
                        
                        for comment in comments:
                            if "AI Code Analysis Report" in comment.get("body", ""):
                                return comment["id"]
            
            return None
        
        except Exception as e:
            logger.error(f"Error finding existing comment: {str(e)}")
            return None
    
    async def _create_pr_comment(self, pr_number: int, body: str):
        """Create new PR comment"""
        try:
            url = f"{self.api_base_url}/repos/{self.repo_owner}/{self.repo_name}/issues/{pr_number}/comments"
            
            comment_data = {"body": body}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self._get_headers(), json=comment_data) as response:
                    if response.status == 201:
                        logger.info("PR comment created successfully")
                    else:
                        logger.error(f"Failed to create PR comment: {response.status}")
        
        except Exception as e:
            logger.error(f"Error creating PR comment: {str(e)}")
    
    async def _update_pr_comment(self, comment_id: int, body: str):
        """Update existing PR comment"""
        try:
            url = f"{self.api_base_url}/repos/{self.repo_owner}/{self.repo_name}/issues/comments/{comment_id}"
            
            comment_data = {"body": body}
            
            async with aiohttp.ClientSession() as session:
                async with session.patch(url, headers=self._get_headers(), json=comment_data) as response:
                    if response.status == 200:
                        logger.info("PR comment updated successfully")
                    else:
                        logger.error(f"Failed to update PR comment: {response.status}")
        
        except Exception as e:
            logger.error(f"Error updating PR comment: {str(e)}")
    
    def _generate_pr_comment(self, analysis_results: Dict) -> str:
        """Generate PR comment content"""
        risk_assessment = analysis_results.get("risk_assessment", {})
        risk_level = risk_assessment.get("risk_level", "unknown")
        risk_score = risk_assessment.get("risk_score", 0)
        
        # Risk level emoji
        risk_emoji = {
            "low": "✅",
            "medium": "⚠️",
            "high": "🚨",
            "critical": "❌"
        }.get(risk_level, "❓")
        
        # Build comment
        comment = [
            "## 🤖 AI Code Analysis Report",
            "",
            f"**Risk Level:** {risk_emoji} {risk_level.upper()}",
            f"**Risk Score:** {risk_score:.1f}/100",
            ""
        ]
        
        # Add recommendation
        if risk_level == "critical":
            comment.append("**❌ NOT RECOMMENDED FOR MERGE**")
            comment.append("Critical issues must be resolved before merging.")
        elif risk_level == "high":
            comment.append("**🚨 REQUIRES CAREFUL REVIEW**")
            comment.append("High-risk changes detected. Please review thoroughly.")
        elif risk_level == "medium":
            comment.append("**⚠️ PROCEED WITH CAUTION**")
            comment.append("Medium-risk changes detected. Consider additional testing.")
        else:
            comment.append("**✅ SAFE TO MERGE**")
            comment.append("Low-risk changes detected.")
        
        comment.append("")
        
        # Add key metrics
        analysis = analysis_results.get("analysis", {})
        tests = analysis_results.get("tests", {})
        test_summary = tests.get("summary", {})
        
        comment.append("### 📊 Key Metrics")
        comment.append("")
        comment.append(f"- **Code Quality:** {analysis.get('quality_score', 0):.1f}/100")
        comment.append(f"- **Test Coverage:** {test_summary.get('coverage_percentage', 0):.1f}%")
        comment.append(f"- **Tests Passed:** {test_summary.get('passed_tests', 0)}/{test_summary.get('total_tests', 0)}")
        comment.append(f"- **Security Issues:** {len(analysis.get('security_issues', []))}")
        comment.append(f"- **Performance Issues:** {len(analysis.get('performance_issues', []))}")
        comment.append("")
        
        # Add top recommendations
        recommendations = risk_assessment.get("recommendations", [])
        if recommendations:
            comment.append("### 💡 Top Recommendations")
            comment.append("")
            for rec in recommendations[:3]:  # Top 3 recommendations
                comment.append(f"- {rec}")
            comment.append("")
        
        # Add performance results if available
        load_testing = analysis_results.get("load_testing", {})
        if load_testing.get("status") != "skipped":
            perf_summary = load_testing.get("summary", {})
            grade = perf_summary.get("performance_grade", "N/A")
            
            comment.append("### ⚡ Performance")
            comment.append("")
            comment.append(f"- **Grade:** {grade}")
            comment.append(f"- **Avg Response Time:** {perf_summary.get('overall_avg_response_time', 0):.0f}ms")
            comment.append(f"- **Failure Rate:** {perf_summary.get('overall_failure_rate', 0):.2f}%")
            comment.append("")
        
        comment.append("---")
        comment.append("*This analysis was generated automatically by the AI Code Analysis Tool*")
        
        return "\n".join(comment)
    
    async def _update_pr_status_check(self, analysis_results: Dict):
        """Update PR status check"""
        try:
            commit_sha = analysis_results.get("commit_hash")
            if not commit_sha:
                return
            
            risk_assessment = analysis_results.get("risk_assessment", {})
            risk_level = risk_assessment.get("risk_level", "unknown")
            
            # Determine status
            state = "success" if risk_level == "low" else "failure" if risk_level in ["high", "critical"] else "pending"
            
            status_data = {
                "state": state,
                "target_url": f"https://github.com/{self.repo_owner}/{self.repo_name}/actions",
                "description": f"Risk level: {risk_level.upper()}",
                "context": "AI Code Analysis"
            }
            
            url = f"{self.api_base_url}/repos/{self.repo_owner}/{self.repo_name}/statuses/{commit_sha}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self._get_headers(), json=status_data) as response:
                    if response.status == 201:
                        logger.info("Status check updated successfully")
                    else:
                        logger.error(f"Failed to update status check: {response.status}")
        
        except Exception as e:
            logger.error(f"Error updating status check: {str(e)}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for GitHub API requests"""
        return {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Code-Analysis-Tool"
        }
    
    def _is_configured(self) -> bool:
        """Check if GitHub integration is properly configured"""
        return bool(self.github_token and self.repo_owner and self.repo_name)