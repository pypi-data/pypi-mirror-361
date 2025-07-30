"""
Load testing module for performance testing
"""

import asyncio
import json
import os
import time
from typing import Dict, List, Any
import aiohttp
import subprocess

from utils.logger import setup_logger

logger = setup_logger(__name__)


class LoadTester:
    """Performs load testing and performance analysis"""
    
    def __init__(self, config):
        self.config = config
        self.test_scenarios = config.get("load_testing.scenarios", [])
        self.default_config = {
            "users": 10,
            "spawn_rate": 2,
            "duration": 60,
            "host": "http://localhost:8000"
        }
    
    async def run_load_tests(self) -> Dict:
        """Run all load testing scenarios"""
        logger.info("Starting load testing")
        
        results = {
            "timestamp": self.config.get_timestamp(),
            "scenarios": {},
            "summary": {},
            "recommendations": []
        }
        
        try:
            # Check if application is running
            if not await self._check_app_availability():
                logger.warning("Application not available for load testing")
                return {
                    "status": "skipped",
                    "reason": "Application not available"
                }
            
            # Run different load testing scenarios
            results["scenarios"]["basic_load"] = await self._run_basic_load_test()
            results["scenarios"]["spike_test"] = await self._run_spike_test()
            results["scenarios"]["stress_test"] = await self._run_stress_test()
            results["scenarios"]["endurance_test"] = await self._run_endurance_test()
            
            # Generate summary and recommendations
            results["summary"] = self._generate_load_test_summary(results["scenarios"])
            results["recommendations"] = self._generate_performance_recommendations(results["scenarios"])
            
            logger.info("Load testing completed")
            return results
            
        except Exception as e:
            logger.error(f"Load testing failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _check_app_availability(self) -> bool:
        """Check if the application is available for testing"""
        host = self.config.get("load_testing.host", self.default_config["host"])
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{host}/health", timeout=5) as response:
                    return response.status == 200
        except Exception:
            # Try basic endpoint
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(host, timeout=5) as response:
                        return response.status < 500
            except Exception:
                return False
    
    async def _run_basic_load_test(self) -> Dict:
        """Run basic load test"""
        logger.info("Running basic load test")
        
        config = {
            "users": self.config.get("load_testing.basic.users", 10),
            "spawn_rate": self.config.get("load_testing.basic.spawn_rate", 2),
            "duration": self.config.get("load_testing.basic.duration", 60),
            "host": self.config.get("load_testing.host", self.default_config["host"])
        }
        
        return await self._run_locust_test(config, "basic_load")
    
    async def _run_spike_test(self) -> Dict:
        """Run spike test"""
        logger.info("Running spike test")
        
        config = {
            "users": self.config.get("load_testing.spike.users", 50),
            "spawn_rate": self.config.get("load_testing.spike.spawn_rate", 10),
            "duration": self.config.get("load_testing.spike.duration", 30),
            "host": self.config.get("load_testing.host", self.default_config["host"])
        }
        
        return await self._run_locust_test(config, "spike_test")
    
    async def _run_stress_test(self) -> Dict:
        """Run stress test"""
        logger.info("Running stress test")
        
        config = {
            "users": self.config.get("load_testing.stress.users", 100),
            "spawn_rate": self.config.get("load_testing.stress.spawn_rate", 5),
            "duration": self.config.get("load_testing.stress.duration", 300),
            "host": self.config.get("load_testing.host", self.default_config["host"])
        }
        
        return await self._run_locust_test(config, "stress_test")
    
    async def _run_endurance_test(self) -> Dict:
        """Run endurance test"""
        logger.info("Running endurance test")
        
        config = {
            "users": self.config.get("load_testing.endurance.users", 20),
            "spawn_rate": self.config.get("load_testing.endurance.spawn_rate", 1),
            "duration": self.config.get("load_testing.endurance.duration", 1800),  # 30 minutes
            "host": self.config.get("load_testing.host", self.default_config["host"])
        }
        
        return await self._run_locust_test(config, "endurance_test")
    
    async def _run_locust_test(self, config: Dict, test_name: str) -> Dict:
        """Run a Locust load test"""
        logger.debug(f"Running Locust test: {test_name}")
        
        # Create locustfile for this test
        locustfile_path = f"locustfile_{test_name}.py"
        self._create_locustfile(locustfile_path, config)
        
        try:
            # Run Locust
            cmd = [
                "locust",
                "-f", locustfile_path,
                "--headless",
                "-u", str(config["users"]),
                "-r", str(config["spawn_rate"]),
                "-t", f"{config['duration']}s",
                "--host", config["host"],
                "--csv", f"locust_{test_name}",
                "--html", f"locust_{test_name}_report.html"
            ]
            
            start_time = time.time()
            result = await self._execute_command(cmd)
            end_time = time.time()
            
            # Parse results
            test_result = {
                "test_name": test_name,
                "config": config,
                "duration": end_time - start_time,
                "status": "completed" if result.get("return_code") == 0 else "failed",
                "metrics": await self._parse_locust_results(f"locust_{test_name}")
            }
            
            if result.get("return_code") != 0:
                test_result["error"] = result.get("stderr", "Unknown error")
            
            return test_result
            
        except Exception as e:
            logger.error(f"Locust test {test_name} failed: {str(e)}")
            return {
                "test_name": test_name,
                "status": "failed",
                "error": str(e)
            }
        finally:
            # Clean up
            if os.path.exists(locustfile_path):
                os.remove(locustfile_path)
    
    def _create_locustfile(self, filename: str, config: Dict):
        """Create a Locustfile for testing"""
        locustfile_content = f'''
from locust import HttpUser, task, between
import random

class LoadTestUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a user starts"""
        pass
    
    @task(3)
    def index_page(self):
        """Test main page"""
        self.client.get("/")
    
    @task(2)
    def health_check(self):
        """Test health endpoint"""
        self.client.get("/health")
    
    @task(1)
    def api_endpoint(self):
        """Test API endpoint"""
        self.client.get("/api/status")
    
    @task(1)
    def static_content(self):
        """Test static content"""
        static_files = ["/favicon.ico", "/robots.txt", "/sitemap.xml"]
        file_path = random.choice(static_files)
        self.client.get(file_path)
    
    @task(1)
    def post_data(self):
        """Test POST request"""
        data = {{"test": "data", "timestamp": "2024-01-01T00:00:00Z"}}
        self.client.post("/api/test", json=data)
'''
        
        with open(filename, "w") as f:
            f.write(locustfile_content)
    
    async def _parse_locust_results(self, prefix: str) -> Dict:
        """Parse Locust CSV results"""
        metrics = {
            "total_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0,
            "min_response_time": 0,
            "max_response_time": 0,
            "requests_per_second": 0,
            "failure_rate": 0
        }
        
        try:
            # Read stats file
            stats_file = f"{prefix}_stats.csv"
            if os.path.exists(stats_file):
                with open(stats_file, "r") as f:
                    lines = f.readlines()
                    
                    if len(lines) > 1:  # Skip header
                        # Parse the "Aggregated" line
                        for line in lines[1:]:
                            if "Aggregated" in line:
                                parts = line.strip().split(",")
                                if len(parts) >= 10:
                                    metrics["total_requests"] = int(parts[1])
                                    metrics["failed_requests"] = int(parts[2])
                                    metrics["average_response_time"] = float(parts[3])
                                    metrics["min_response_time"] = float(parts[4])
                                    metrics["max_response_time"] = float(parts[5])
                                    metrics["requests_per_second"] = float(parts[8])
                                    
                                    if metrics["total_requests"] > 0:
                                        metrics["failure_rate"] = (metrics["failed_requests"] / metrics["total_requests"]) * 100
                                break
            
            # Read failures file
            failures_file = f"{prefix}_failures.csv"
            if os.path.exists(failures_file):
                with open(failures_file, "r") as f:
                    failure_lines = f.readlines()
                    metrics["failure_details"] = [line.strip() for line in failure_lines[1:]]  # Skip header
            
        except Exception as e:
            logger.error(f"Error parsing Locust results: {str(e)}")
        
        return metrics
    
    async def _execute_command(self, cmd: List[str]) -> Dict:
        """Execute a command and return result"""
        logger.debug(f"Executing command: {' '.join(cmd)}")
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.config.get("repository.path", ".")
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "return_code": process.returncode,
                "stdout": stdout.decode("utf-8", errors="ignore"),
                "stderr": stderr.decode("utf-8", errors="ignore")
            }
            
        except Exception as e:
            logger.error(f"Command execution failed: {str(e)}")
            return {
                "return_code": -1,
                "error": str(e)
            }
    
    def _generate_load_test_summary(self, scenarios: Dict) -> Dict:
        """Generate load test summary"""
        summary = {
            "total_scenarios": len(scenarios),
            "passed_scenarios": 0,
            "failed_scenarios": 0,
            "overall_rps": 0,
            "overall_avg_response_time": 0,
            "overall_failure_rate": 0,
            "performance_grade": "unknown"
        }
        
        total_requests = 0
        total_response_time = 0
        total_failures = 0
        
        for scenario_name, scenario_result in scenarios.items():
            if scenario_result.get("status") == "completed":
                summary["passed_scenarios"] += 1
                
                metrics = scenario_result.get("metrics", {})
                scenario_requests = metrics.get("total_requests", 0)
                
                if scenario_requests > 0:
                    total_requests += scenario_requests
                    total_response_time += metrics.get("average_response_time", 0) * scenario_requests
                    total_failures += metrics.get("failed_requests", 0)
                    summary["overall_rps"] += metrics.get("requests_per_second", 0)
            else:
                summary["failed_scenarios"] += 1
        
        # Calculate averages
        if total_requests > 0:
            summary["overall_avg_response_time"] = total_response_time / total_requests
            summary["overall_failure_rate"] = (total_failures / total_requests) * 100
        
        # Calculate performance grade
        summary["performance_grade"] = self._calculate_performance_grade(summary)
        
        return summary
    
    def _calculate_performance_grade(self, summary: Dict) -> str:
        """Calculate overall performance grade"""
        score = 100
        
        # Deduct points for high response times
        avg_response_time = summary.get("overall_avg_response_time", 0)
        if avg_response_time > 1000:  # > 1 second
            score -= 30
        elif avg_response_time > 500:  # > 500ms
            score -= 15
        elif avg_response_time > 200:  # > 200ms
            score -= 5
        
        # Deduct points for failures
        failure_rate = summary.get("overall_failure_rate", 0)
        if failure_rate > 5:  # > 5% failure rate
            score -= 40
        elif failure_rate > 1:  # > 1% failure rate
            score -= 20
        elif failure_rate > 0.1:  # > 0.1% failure rate
            score -= 10
        
        # Deduct points for low RPS
        rps = summary.get("overall_rps", 0)
        if rps < 10:
            score -= 20
        elif rps < 50:
            score -= 10
        
        # Deduct points for failed scenarios
        failed_scenarios = summary.get("failed_scenarios", 0)
        score -= failed_scenarios * 25
        
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _generate_performance_recommendations(self, scenarios: Dict) -> List[str]:
        """Generate performance recommendations based on test results"""
        recommendations = []
        
        for scenario_name, scenario_result in scenarios.items():
            if scenario_result.get("status") != "completed":
                continue
            
            metrics = scenario_result.get("metrics", {})
            
            # Response time recommendations
            avg_response_time = metrics.get("average_response_time", 0)
            if avg_response_time > 1000:
                recommendations.append(f"High response time in {scenario_name} ({avg_response_time}ms). Consider optimizing database queries, adding caching, or scaling infrastructure.")
            elif avg_response_time > 500:
                recommendations.append(f"Moderate response time in {scenario_name} ({avg_response_time}ms). Consider adding caching or optimizing slow endpoints.")
            
            # Failure rate recommendations
            failure_rate = metrics.get("failure_rate", 0)
            if failure_rate > 5:
                recommendations.append(f"High failure rate in {scenario_name} ({failure_rate}%). Check for errors, timeouts, or resource constraints.")
            elif failure_rate > 1:
                recommendations.append(f"Moderate failure rate in {scenario_name} ({failure_rate}%). Monitor error logs and consider adding retry logic.")
            
            # RPS recommendations
            rps = metrics.get("requests_per_second", 0)
            if rps < 10:
                recommendations.append(f"Low throughput in {scenario_name} ({rps} RPS). Consider horizontal scaling or performance optimization.")
            
            # Memory/resource recommendations
            max_response_time = metrics.get("max_response_time", 0)
            if max_response_time > avg_response_time * 5:
                recommendations.append(f"High response time variance in {scenario_name}. Check for memory leaks, garbage collection issues, or resource contention.")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Performance looks good! Consider adding more comprehensive load testing scenarios.")
        
        return recommendations