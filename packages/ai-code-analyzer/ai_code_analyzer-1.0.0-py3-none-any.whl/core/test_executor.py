"""
Test executor module for running various types of tests
"""

import asyncio
import json
import os
import subprocess
from typing import Dict, List, Any
from pathlib import Path

from utils.logger import setup_logger

logger = setup_logger(__name__)


class TestExecutor:
    """Executes various types of tests and collects results"""
    
    def __init__(self, config):
        self.config = config
        self.repo_path = config.get("repository.path", ".")
        self.test_frameworks = {
            'python': ['pytest', 'unittest', 'nose2'],
            'javascript': ['jest', 'mocha', 'cypress', 'playwright'],
            'java': ['junit', 'testng', 'maven', 'gradle'],
            'go': ['go test'],
            'rust': ['cargo test'],
            'ruby': ['rspec', 'minitest'],
            'php': ['phpunit'],
            'swift': ['swift test'],
            'kotlin': ['gradle test'],
            'scala': ['sbt test']
        }
    
    async def run_all_tests(self) -> Dict:
        """Run all available tests"""
        logger.info("Starting test execution")
        
        test_results = {
            "timestamp": self.config.get_timestamp(),
            "unit_tests": {},
            "integration_tests": {},
            "e2e_tests": {},
            "performance_tests": {},
            "security_tests": {},
            "coverage": {},
            "overall_status": "unknown",
            "summary": {}
        }
        
        try:
            # Detect available test frameworks
            available_frameworks = self._detect_test_frameworks()
            logger.info(f"Detected test frameworks: {available_frameworks}")
            
            # Run unit tests
            test_results["unit_tests"] = await self._run_unit_tests(available_frameworks)
            
            # Run integration tests
            test_results["integration_tests"] = await self._run_integration_tests(available_frameworks)
            
            # Run end-to-end tests
            test_results["e2e_tests"] = await self._run_e2e_tests(available_frameworks)
            
            # Run performance tests
            test_results["performance_tests"] = await self._run_performance_tests()
            
            # Run security tests
            test_results["security_tests"] = await self._run_security_tests()
            
            # Generate coverage report
            test_results["coverage"] = await self._generate_coverage_report(available_frameworks)
            
            # Calculate overall status
            test_results["overall_status"] = self._calculate_overall_status(test_results)
            
            # Generate summary
            test_results["summary"] = self._generate_test_summary(test_results)
            
            logger.info("Test execution completed")
            return test_results
            
        except Exception as e:
            logger.error(f"Test execution failed: {str(e)}")
            test_results["error"] = str(e)
            test_results["overall_status"] = "failed"
            return test_results
    
    def _detect_test_frameworks(self) -> Dict[str, List[str]]:
        """Detect available test frameworks"""
        available = {}
        
        # Check for Python test frameworks
        if self._file_exists("pytest.ini") or self._file_exists("setup.cfg") or self._file_exists("pyproject.toml"):
            available["python"] = ["pytest"]
        elif self._directory_exists("tests") and self._has_python_files("tests"):
            available["python"] = ["unittest"]
        
        # Check for JavaScript test frameworks
        if self._file_exists("package.json"):
            package_json = self._read_package_json()
            if package_json:
                deps = {**package_json.get("dependencies", {}), **package_json.get("devDependencies", {})}
                js_frameworks = []
                
                if "jest" in deps:
                    js_frameworks.append("jest")
                if "mocha" in deps:
                    js_frameworks.append("mocha")
                if "cypress" in deps:
                    js_frameworks.append("cypress")
                if "playwright" in deps:
                    js_frameworks.append("playwright")
                
                if js_frameworks:
                    available["javascript"] = js_frameworks
        
        # Check for Java test frameworks
        if self._file_exists("pom.xml"):
            available["java"] = ["maven"]
        elif self._file_exists("build.gradle") or self._file_exists("build.gradle.kts"):
            available["java"] = ["gradle"]
        
        # Check for Go tests
        if self._has_go_test_files():
            available["go"] = ["go test"]
        
        # Check for Rust tests
        if self._file_exists("Cargo.toml"):
            available["rust"] = ["cargo test"]
        
        return available
    
    async def _run_unit_tests(self, frameworks: Dict[str, List[str]]) -> Dict:
        """Run unit tests for all detected frameworks"""
        logger.info("Running unit tests")
        results = {}
        
        for language, framework_list in frameworks.items():
            for framework in framework_list:
                try:
                    result = await self._run_test_framework(language, framework, "unit")
                    results[f"{language}_{framework}"] = result
                except Exception as e:
                    logger.error(f"Error running {language} {framework} unit tests: {str(e)}")
                    results[f"{language}_{framework}"] = {"error": str(e), "status": "failed"}
        
        return results
    
    async def _run_integration_tests(self, frameworks: Dict[str, List[str]]) -> Dict:
        """Run integration tests"""
        logger.info("Running integration tests")
        results = {}
        
        for language, framework_list in frameworks.items():
            for framework in framework_list:
                try:
                    result = await self._run_test_framework(language, framework, "integration")
                    results[f"{language}_{framework}"] = result
                except Exception as e:
                    logger.error(f"Error running {language} {framework} integration tests: {str(e)}")
                    results[f"{language}_{framework}"] = {"error": str(e), "status": "failed"}
        
        return results
    
    async def _run_e2e_tests(self, frameworks: Dict[str, List[str]]) -> Dict:
        """Run end-to-end tests"""
        logger.info("Running end-to-end tests")
        results = {}
        
        # Check for specific e2e frameworks
        if "javascript" in frameworks:
            for framework in frameworks["javascript"]:
                if framework in ["cypress", "playwright"]:
                    try:
                        result = await self._run_e2e_framework(framework)
                        results[framework] = result
                    except Exception as e:
                        logger.error(f"Error running {framework} e2e tests: {str(e)}")
                        results[framework] = {"error": str(e), "status": "failed"}
        
        return results
    
    async def _run_performance_tests(self) -> Dict:
        """Run performance tests"""
        logger.info("Running performance tests")
        results = {}
        
        # Check for performance test tools
        if self._file_exists("locustfile.py"):
            results["locust"] = await self._run_locust_tests()
        
        if self._file_exists("artillery.yml") or self._file_exists("artillery.yaml"):
            results["artillery"] = await self._run_artillery_tests()
        
        # Run benchmark tests if available
        results["benchmarks"] = await self._run_benchmark_tests()
        
        return results
    
    async def _run_security_tests(self) -> Dict:
        """Run security tests"""
        logger.info("Running security tests")
        results = {}
        
        # Run various security scanners
        results["bandit"] = await self._run_bandit_scan()
        results["safety"] = await self._run_safety_scan()
        results["semgrep"] = await self._run_semgrep_scan()
        results["dependency_check"] = await self._run_dependency_check()
        
        return results
    
    async def _run_test_framework(self, language: str, framework: str, test_type: str) -> Dict:
        """Run tests for a specific framework"""
        logger.debug(f"Running {language} {framework} {test_type} tests")
        
        result = {
            "framework": framework,
            "language": language,
            "test_type": test_type,
            "status": "unknown",
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "tests_skipped": 0,
            "duration": 0,
            "output": ""
        }
        
        try:
            if language == "python" and framework == "pytest":
                return await self._run_pytest(test_type)
            elif language == "python" and framework == "unittest":
                return await self._run_unittest(test_type)
            elif language == "javascript" and framework == "jest":
                return await self._run_jest(test_type)
            elif language == "javascript" and framework == "mocha":
                return await self._run_mocha(test_type)
            elif language == "java" and framework == "maven":
                return await self._run_maven_tests(test_type)
            elif language == "java" and framework == "gradle":
                return await self._run_gradle_tests(test_type)
            elif language == "go" and framework == "go test":
                return await self._run_go_tests(test_type)
            elif language == "rust" and framework == "cargo test":
                return await self._run_cargo_tests(test_type)
            
        except Exception as e:
            logger.error(f"Error running {framework} tests: {str(e)}")
            result["error"] = str(e)
            result["status"] = "failed"
        
        return result
    
    async def _run_pytest(self, test_type: str) -> Dict:
        """Run pytest"""
        test_path = self._get_test_path(test_type)
        
        cmd = ["pytest", test_path, "--json-report", "--json-report-file=pytest-report.json", "-v"]
        
        if test_type == "unit":
            cmd.extend(["-m", "not integration"])
        elif test_type == "integration":
            cmd.extend(["-m", "integration"])
        
        result = await self._execute_command(cmd)
        
        # Parse pytest JSON report
        if os.path.exists("pytest-report.json"):
            with open("pytest-report.json", "r") as f:
                pytest_report = json.load(f)
            
            result.update({
                "tests_run": pytest_report.get("summary", {}).get("total", 0),
                "tests_passed": pytest_report.get("summary", {}).get("passed", 0),
                "tests_failed": pytest_report.get("summary", {}).get("failed", 0),
                "tests_skipped": pytest_report.get("summary", {}).get("skipped", 0),
                "duration": pytest_report.get("duration", 0)
            })
        
        return result
    
    async def _run_jest(self, test_type: str) -> Dict:
        """Run Jest tests"""
        cmd = ["npx", "jest", "--json", "--outputFile=jest-report.json"]
        
        if test_type == "unit":
            cmd.extend(["--testPathPattern=unit"])
        elif test_type == "integration":
            cmd.extend(["--testPathPattern=integration"])
        
        result = await self._execute_command(cmd)
        
        # Parse Jest JSON report
        if os.path.exists("jest-report.json"):
            with open("jest-report.json", "r") as f:
                jest_report = json.load(f)
            
            result.update({
                "tests_run": jest_report.get("numTotalTests", 0),
                "tests_passed": jest_report.get("numPassedTests", 0),
                "tests_failed": jest_report.get("numFailedTests", 0),
                "tests_skipped": jest_report.get("numPendingTests", 0),
                "duration": jest_report.get("testResults", [{}])[0].get("perfStats", {}).get("runtime", 0)
            })
        
        return result
    
    async def _run_go_tests(self, test_type: str) -> Dict:
        """Run Go tests"""
        cmd = ["go", "test", "-json", "./..."]
        
        if test_type == "unit":
            cmd.extend(["-short"])
        
        result = await self._execute_command(cmd)
        
        # Parse Go test output
        if result.get("stdout"):
            lines = result["stdout"].split("\n")
            tests_run = 0
            tests_passed = 0
            tests_failed = 0
            
            for line in lines:
                if line.startswith('{"Time"'):
                    try:
                        test_result = json.loads(line)
                        if test_result.get("Action") == "run":
                            tests_run += 1
                        elif test_result.get("Action") == "pass":
                            tests_passed += 1
                        elif test_result.get("Action") == "fail":
                            tests_failed += 1
                    except json.JSONDecodeError:
                        pass
            
            result.update({
                "tests_run": tests_run,
                "tests_passed": tests_passed,
                "tests_failed": tests_failed,
                "tests_skipped": 0
            })
        
        return result
    
    async def _execute_command(self, cmd: List[str]) -> Dict:
        """Execute a command and return result"""
        logger.debug(f"Executing command: {' '.join(cmd)}")
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.repo_path
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "status": "passed" if process.returncode == 0 else "failed",
                "return_code": process.returncode,
                "stdout": stdout.decode("utf-8", errors="ignore"),
                "stderr": stderr.decode("utf-8", errors="ignore")
            }
            
        except Exception as e:
            logger.error(f"Command execution failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _get_test_path(self, test_type: str) -> str:
        """Get test path based on test type"""
        if test_type == "unit":
            return "tests/unit" if self._directory_exists("tests/unit") else "tests"
        elif test_type == "integration":
            return "tests/integration" if self._directory_exists("tests/integration") else "tests"
        else:
            return "tests"
    
    def _file_exists(self, path: str) -> bool:
        """Check if file exists"""
        return os.path.exists(os.path.join(self.repo_path, path))
    
    def _directory_exists(self, path: str) -> bool:
        """Check if directory exists"""
        return os.path.isdir(os.path.join(self.repo_path, path))
    
    def _has_python_files(self, path: str) -> bool:
        """Check if directory has Python files"""
        full_path = os.path.join(self.repo_path, path)
        if not os.path.exists(full_path):
            return False
        
        for file in os.listdir(full_path):
            if file.endswith('.py'):
                return True
        return False
    
    def _has_go_test_files(self) -> bool:
        """Check if there are Go test files"""
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith('_test.go'):
                    return True
        return False
    
    def _read_package_json(self) -> Dict:
        """Read package.json file"""
        try:
            with open(os.path.join(self.repo_path, "package.json"), "r") as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _calculate_overall_status(self, test_results: Dict) -> str:
        """Calculate overall test status"""
        all_results = []
        
        for category in ["unit_tests", "integration_tests", "e2e_tests", "performance_tests", "security_tests"]:
            if category in test_results:
                for test_name, result in test_results[category].items():
                    all_results.append(result.get("status", "unknown"))
        
        if "failed" in all_results:
            return "failed"
        elif "unknown" in all_results:
            return "unknown"
        elif all_results:
            return "passed"
        else:
            return "no_tests"
    
    def _generate_test_summary(self, test_results: Dict) -> Dict:
        """Generate test summary"""
        summary = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0,
            "total_duration": 0,
            "coverage_percentage": 0
        }
        
        for category in ["unit_tests", "integration_tests", "e2e_tests", "performance_tests", "security_tests"]:
            if category in test_results:
                for test_name, result in test_results[category].items():
                    summary["total_tests"] += result.get("tests_run", 0)
                    summary["passed_tests"] += result.get("tests_passed", 0)
                    summary["failed_tests"] += result.get("tests_failed", 0)
                    summary["skipped_tests"] += result.get("tests_skipped", 0)
                    summary["total_duration"] += result.get("duration", 0)
        
        if test_results.get("coverage"):
            summary["coverage_percentage"] = test_results["coverage"].get("percentage", 0)
        
        return summary
    
    async def _generate_coverage_report(self, frameworks: Dict[str, List[str]]) -> Dict:
        """Generate code coverage report"""
        coverage_result = {
            "percentage": 0,
            "lines_covered": 0,
            "lines_total": 0,
            "by_file": {}
        }
        
        # Try to generate coverage for each language
        if "python" in frameworks:
            python_coverage = await self._generate_python_coverage()
            if python_coverage:
                coverage_result.update(python_coverage)
        
        if "javascript" in frameworks:
            js_coverage = await self._generate_javascript_coverage()
            if js_coverage:
                coverage_result.update(js_coverage)
        
        return coverage_result
    
    async def _generate_python_coverage(self) -> Dict:
        """Generate Python coverage report"""
        try:
            cmd = ["coverage", "run", "-m", "pytest"]
            await self._execute_command(cmd)
            
            cmd = ["coverage", "report", "--format=json"]
            result = await self._execute_command(cmd)
            
            if result.get("stdout"):
                coverage_data = json.loads(result["stdout"])
                return {
                    "percentage": coverage_data.get("totals", {}).get("percent_covered", 0),
                    "lines_covered": coverage_data.get("totals", {}).get("covered_lines", 0),
                    "lines_total": coverage_data.get("totals", {}).get("num_statements", 0)
                }
        except Exception as e:
            logger.debug(f"Python coverage generation failed: {str(e)}")
        
        return {}
    
    async def _generate_javascript_coverage(self) -> Dict:
        """Generate JavaScript coverage report"""
        try:
            cmd = ["npx", "jest", "--coverage", "--coverageReporters=json"]
            result = await self._execute_command(cmd)
            
            if os.path.exists("coverage/coverage-final.json"):
                with open("coverage/coverage-final.json", "r") as f:
                    coverage_data = json.load(f)
                
                # Calculate overall coverage
                total_lines = sum(len(file_data["s"]) for file_data in coverage_data.values())
                covered_lines = sum(
                    sum(1 for count in file_data["s"].values() if count > 0)
                    for file_data in coverage_data.values()
                )
                
                return {
                    "percentage": (covered_lines / total_lines * 100) if total_lines > 0 else 0,
                    "lines_covered": covered_lines,
                    "lines_total": total_lines
                }
        except Exception as e:
            logger.debug(f"JavaScript coverage generation failed: {str(e)}")
        
        return {}
    
    async def _run_bandit_scan(self) -> Dict:
        """Run Bandit security scan for Python"""
        try:
            cmd = ["bandit", "-r", ".", "-f", "json", "-o", "bandit-report.json"]
            result = await self._execute_command(cmd)
            
            if os.path.exists("bandit-report.json"):
                with open("bandit-report.json", "r") as f:
                    bandit_report = json.load(f)
                
                return {
                    "status": "completed",
                    "issues_found": len(bandit_report.get("results", [])),
                    "high_severity": len([r for r in bandit_report.get("results", []) if r.get("issue_severity") == "HIGH"]),
                    "medium_severity": len([r for r in bandit_report.get("results", []) if r.get("issue_severity") == "MEDIUM"]),
                    "low_severity": len([r for r in bandit_report.get("results", []) if r.get("issue_severity") == "LOW"])
                }
        except Exception as e:
            logger.debug(f"Bandit scan failed: {str(e)}")
        
        return {"status": "not_available"}
    
    async def _run_safety_scan(self) -> Dict:
        """Run Safety scan for Python dependencies"""
        try:
            cmd = ["safety", "check", "--json"]
            result = await self._execute_command(cmd)
            
            if result.get("stdout"):
                safety_report = json.loads(result["stdout"])
                return {
                    "status": "completed",
                    "vulnerabilities_found": len(safety_report)
                }
        except Exception as e:
            logger.debug(f"Safety scan failed: {str(e)}")
        
        return {"status": "not_available"}
    
    async def _run_semgrep_scan(self) -> Dict:
        """Run Semgrep scan"""
        try:
            cmd = ["semgrep", "--config=auto", "--json", "."]
            result = await self._execute_command(cmd)
            
            if result.get("stdout"):
                semgrep_report = json.loads(result["stdout"])
                return {
                    "status": "completed",
                    "findings": len(semgrep_report.get("results", [])),
                    "errors": len(semgrep_report.get("errors", []))
                }
        except Exception as e:
            logger.debug(f"Semgrep scan failed: {str(e)}")
        
        return {"status": "not_available"}
    
    async def _run_dependency_check(self) -> Dict:
        """Run dependency vulnerability check"""
        # This would implement dependency checking for different languages
        return {"status": "not_implemented"}
    
    async def _run_locust_tests(self) -> Dict:
        """Run Locust performance tests"""
        try:
            cmd = ["locust", "-f", "locustfile.py", "--headless", "-u", "10", "-r", "2", "-t", "30s", "--html", "locust-report.html"]
            result = await self._execute_command(cmd)
            
            return {
                "status": "completed" if result.get("return_code") == 0 else "failed",
                "output": result.get("stdout", "")
            }
        except Exception as e:
            logger.debug(f"Locust tests failed: {str(e)}")
        
        return {"status": "not_available"}
    
    async def _run_artillery_tests(self) -> Dict:
        """Run Artillery performance tests"""
        try:
            cmd = ["artillery", "run", "artillery.yml"]
            result = await self._execute_command(cmd)
            
            return {
                "status": "completed" if result.get("return_code") == 0 else "failed",
                "output": result.get("stdout", "")
            }
        except Exception as e:
            logger.debug(f"Artillery tests failed: {str(e)}")
        
        return {"status": "not_available"}
    
    async def _run_benchmark_tests(self) -> Dict:
        """Run benchmark tests"""
        # This would implement benchmark testing for different languages
        return {"status": "not_implemented"}
    
    async def _run_e2e_framework(self, framework: str) -> Dict:
        """Run end-to-end tests with specific framework"""
        if framework == "cypress":
            return await self._run_cypress_tests()
        elif framework == "playwright":
            return await self._run_playwright_tests()
        
        return {"status": "not_supported"}
    
    async def _run_cypress_tests(self) -> Dict:
        """Run Cypress tests"""
        try:
            cmd = ["npx", "cypress", "run", "--reporter", "json"]
            result = await self._execute_command(cmd)
            
            return {
                "status": "completed" if result.get("return_code") == 0 else "failed",
                "output": result.get("stdout", "")
            }
        except Exception as e:
            logger.debug(f"Cypress tests failed: {str(e)}")
        
        return {"status": "not_available"}
    
    async def _run_playwright_tests(self) -> Dict:
        """Run Playwright tests"""
        try:
            cmd = ["npx", "playwright", "test", "--reporter=json"]
            result = await self._execute_command(cmd)
            
            return {
                "status": "completed" if result.get("return_code") == 0 else "failed",
                "output": result.get("stdout", "")
            }
        except Exception as e:
            logger.debug(f"Playwright tests failed: {str(e)}")
        
        return {"status": "not_available"}
    
    async def _run_unittest(self, test_type: str) -> Dict:
        """Run Python unittest"""
        try:
            cmd = ["python", "-m", "unittest", "discover", "-s", "tests", "-v"]
            result = await self._execute_command(cmd)
            
            return {
                "status": "completed" if result.get("return_code") == 0 else "failed",
                "output": result.get("stdout", "")
            }
        except Exception as e:
            logger.debug(f"unittest failed: {str(e)}")
        
        return {"status": "not_available"}
    
    async def _run_mocha(self, test_type: str) -> Dict:
        """Run Mocha tests"""
        try:
            cmd = ["npx", "mocha", "--reporter", "json"]
            result = await self._execute_command(cmd)
            
            return {
                "status": "completed" if result.get("return_code") == 0 else "failed",
                "output": result.get("stdout", "")
            }
        except Exception as e:
            logger.debug(f"Mocha tests failed: {str(e)}")
        
        return {"status": "not_available"}
    
    async def _run_maven_tests(self, test_type: str) -> Dict:
        """Run Maven tests"""
        try:
            cmd = ["mvn", "test"]
            result = await self._execute_command(cmd)
            
            return {
                "status": "completed" if result.get("return_code") == 0 else "failed",
                "output": result.get("stdout", "")
            }
        except Exception as e:
            logger.debug(f"Maven tests failed: {str(e)}")
        
        return {"status": "not_available"}
    
    async def _run_gradle_tests(self, test_type: str) -> Dict:
        """Run Gradle tests"""
        try:
            cmd = ["./gradlew", "test"]
            result = await self._execute_command(cmd)
            
            return {
                "status": "completed" if result.get("return_code") == 0 else "failed",
                "output": result.get("stdout", "")
            }
        except Exception as e:
            logger.debug(f"Gradle tests failed: {str(e)}")
        
        return {"status": "not_available"}
    
    async def _run_cargo_tests(self, test_type: str) -> Dict:
        """Run Cargo tests"""
        try:
            cmd = ["cargo", "test"]
            result = await self._execute_command(cmd)
            
            return {
                "status": "completed" if result.get("return_code") == 0 else "failed",
                "output": result.get("stdout", "")
            }
        except Exception as e:
            logger.debug(f"Cargo tests failed: {str(e)}")
        
        return {"status": "not_available"}