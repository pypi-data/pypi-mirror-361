"""
AI model for risk assessment and analysis
"""

import json
import os
from typing import Dict, List, Any, Optional
import openai
import anthropic

from utils.logger import setup_logger

logger = setup_logger(__name__)


class AIRiskAssessment:
    """AI-powered risk assessment for code changes"""
    
    def __init__(self, config):
        self.config = config
        self.openai_client = None
        self.anthropic_client = None
        
        # Initialize AI clients
        self._initialize_ai_clients()
        
        # Risk assessment criteria
        self.risk_criteria = {
            "security": {
                "weight": 0.3,
                "critical_keywords": ["password", "api_key", "token", "auth", "crypto", "hash", "encrypt", "decrypt"]
            },
            "performance": {
                "weight": 0.2,
                "critical_keywords": ["loop", "query", "database", "cache", "memory", "cpu", "thread", "async"]
            },
            "reliability": {
                "weight": 0.25,
                "critical_keywords": ["exception", "error", "try", "catch", "null", "undefined", "panic", "assert"]
            },
            "maintainability": {
                "weight": 0.15,
                "critical_keywords": ["refactor", "deprecated", "legacy", "todo", "fixme", "hack", "workaround"]
            },
            "testing": {
                "weight": 0.1,
                "critical_keywords": ["test", "mock", "stub", "coverage", "assertion", "verify", "validate"]
            }
        }
    
    def _initialize_ai_clients(self):
        """Initialize AI clients"""
        try:
            # OpenAI client
            openai_api_key = self.config.get("ai.openai_api_key") or os.getenv("OPENAI_API_KEY")
            if openai_api_key:
                self.openai_client = openai.OpenAI(api_key=openai_api_key)
                logger.info("OpenAI client initialized")
            
            # Anthropic client
            anthropic_api_key = self.config.get("ai.anthropic_api_key") or os.getenv("ANTHROPIC_API_KEY")
            if anthropic_api_key:
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
                logger.info("Anthropic client initialized")
            
            if not self.openai_client and not self.anthropic_client:
                logger.warning("No AI clients initialized. Risk assessment will use rule-based analysis only.")
        
        except Exception as e:
            logger.error(f"Error initializing AI clients: {str(e)}")
    
    async def assess_risk(self, analysis_results: Dict) -> Dict:
        """Perform comprehensive risk assessment"""
        logger.info("Starting AI risk assessment")
        
        risk_assessment = {
            "timestamp": self.config.get_timestamp(),
            "risk_level": "unknown",
            "risk_score": 0,
            "risk_factors": {},
            "recommendations": [],
            "detailed_analysis": {},
            "confidence": 0
        }
        
        try:
            # Rule-based risk assessment
            rule_based_risk = await self._rule_based_assessment(analysis_results)
            
            # AI-powered risk assessment
            ai_risk = await self._ai_powered_assessment(analysis_results)
            
            # Combine assessments
            risk_assessment = self._combine_assessments(rule_based_risk, ai_risk)
            
            # Generate recommendations
            risk_assessment["recommendations"] = await self._generate_recommendations(risk_assessment)
            
            logger.info(f"Risk assessment completed. Risk level: {risk_assessment['risk_level']}")
            return risk_assessment
            
        except Exception as e:
            logger.error(f"Risk assessment failed: {str(e)}")
            return {
                "error": str(e),
                "risk_level": "high",  # Default to high risk on error
                "risk_score": 100
            }
    
    async def _rule_based_assessment(self, analysis_results: Dict) -> Dict:
        """Perform rule-based risk assessment"""
        logger.debug("Performing rule-based risk assessment")
        
        risk_factors = {}
        total_score = 0
        
        # Analyze code analysis results
        if "analysis" in analysis_results:
            analysis = analysis_results["analysis"]
            
            # Security risk
            security_issues = len(analysis.get("security_issues", []))
            risk_factors["security"] = {
                "score": min(security_issues * 20, 100),
                "issues": security_issues,
                "weight": self.risk_criteria["security"]["weight"]
            }
            
            # Performance risk
            performance_issues = len(analysis.get("performance_issues", []))
            risk_factors["performance"] = {
                "score": min(performance_issues * 15, 100),
                "issues": performance_issues,
                "weight": self.risk_criteria["performance"]["weight"]
            }
            
            # Code quality risk
            quality_score = analysis.get("quality_score", 100)
            risk_factors["quality"] = {
                "score": max(0, 100 - quality_score),
                "quality_score": quality_score,
                "weight": self.risk_criteria["maintainability"]["weight"]
            }
            
            # Complexity risk
            complexity_metrics = analysis.get("complexity_metrics", {})
            avg_complexity = sum(complexity_metrics.values()) / len(complexity_metrics) if complexity_metrics else 0
            risk_factors["complexity"] = {
                "score": min(max(0, (avg_complexity - 10) * 10), 100),
                "average_complexity": avg_complexity,
                "weight": self.risk_criteria["reliability"]["weight"]
            }
        
        # Analyze test results
        if "tests" in analysis_results:
            tests = analysis_results["tests"]
            
            # Test coverage risk
            coverage = tests.get("coverage", {}).get("percentage", 0)
            risk_factors["test_coverage"] = {
                "score": max(0, 100 - coverage),
                "coverage": coverage,
                "weight": self.risk_criteria["testing"]["weight"]
            }
            
            # Test failure risk
            test_summary = tests.get("summary", {})
            total_tests = test_summary.get("total_tests", 0)
            failed_tests = test_summary.get("failed_tests", 0)
            
            if total_tests > 0:
                failure_rate = (failed_tests / total_tests) * 100
                risk_factors["test_failures"] = {
                    "score": failure_rate * 2,  # Double the impact
                    "failure_rate": failure_rate,
                    "weight": self.risk_criteria["reliability"]["weight"]
                }
        
        # Analyze load testing results
        if "load_testing" in analysis_results:
            load_testing = analysis_results["load_testing"]
            
            if "summary" in load_testing:
                summary = load_testing["summary"]
                failure_rate = summary.get("overall_failure_rate", 0)
                avg_response_time = summary.get("overall_avg_response_time", 0)
                
                performance_score = 0
                if failure_rate > 5:
                    performance_score += 40
                elif failure_rate > 1:
                    performance_score += 20
                
                if avg_response_time > 1000:
                    performance_score += 30
                elif avg_response_time > 500:
                    performance_score += 15
                
                risk_factors["load_performance"] = {
                    "score": min(performance_score, 100),
                    "failure_rate": failure_rate,
                    "avg_response_time": avg_response_time,
                    "weight": self.risk_criteria["performance"]["weight"]
                }
        
        # Calculate weighted total score
        for factor_name, factor_data in risk_factors.items():
            weighted_score = factor_data["score"] * factor_data["weight"]
            total_score += weighted_score
        
        risk_level = self._calculate_risk_level(total_score)
        
        return {
            "method": "rule_based",
            "risk_score": total_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "confidence": 0.8  # Rule-based has high confidence
        }
    
    async def _ai_powered_assessment(self, analysis_results: Dict) -> Dict:
        """Perform AI-powered risk assessment"""
        logger.debug("Performing AI-powered risk assessment")
        
        if not self.openai_client and not self.anthropic_client:
            logger.warning("No AI clients available for AI-powered assessment")
            return {
                "method": "ai_powered",
                "risk_score": 0,
                "risk_level": "unknown",
                "confidence": 0,
                "error": "No AI clients available"
            }
        
        try:
            # Prepare data for AI analysis
            ai_prompt = self._prepare_ai_prompt(analysis_results)
            
            # Get AI assessment
            ai_response = await self._query_ai_model(ai_prompt)
            
            # Parse AI response
            ai_assessment = self._parse_ai_response(ai_response)
            
            return ai_assessment
            
        except Exception as e:
            logger.error(f"AI-powered assessment failed: {str(e)}")
            return {
                "method": "ai_powered",
                "risk_score": 0,
                "risk_level": "unknown",
                "confidence": 0,
                "error": str(e)
            }
    
    def _prepare_ai_prompt(self, analysis_results: Dict) -> str:
        """Prepare prompt for AI model"""
        prompt = f"""
You are a senior software engineer and security expert. Analyze the following code analysis results and provide a comprehensive risk assessment.

Analysis Results:
{json.dumps(analysis_results, indent=2)}

Please provide a risk assessment with the following structure:
1. Overall risk level (low, medium, high, critical)
2. Risk score (0-100)
3. Key risk factors and their impact
4. Specific recommendations for mitigation
5. Confidence level (0-1)

Focus on:
- Security vulnerabilities and potential exploits
- Performance bottlenecks and scalability issues
- Code quality and maintainability concerns
- Test coverage and reliability
- Breaking changes or compatibility issues

Provide your assessment in JSON format:
{{
    "risk_level": "low|medium|high|critical",
    "risk_score": 0-100,
    "key_risks": ["list of key risks"],
    "recommendations": ["list of specific recommendations"],
    "confidence": 0-1,
    "reasoning": "detailed explanation"
}}
"""
        return prompt
    
    async def _query_ai_model(self, prompt: str) -> str:
        """Query AI model for assessment"""
        try:
            if self.openai_client:
                response = await self._query_openai(prompt)
                if response:
                    return response
            
            if self.anthropic_client:
                response = await self._query_anthropic(prompt)
                if response:
                    return response
            
            raise Exception("No AI model responded successfully")
            
        except Exception as e:
            logger.error(f"AI model query failed: {str(e)}")
            raise
    
    async def _query_openai(self, prompt: str) -> Optional[str]:
        """Query OpenAI model"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a senior software engineer and security expert specializing in code risk assessment."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI query failed: {str(e)}")
            return None
    
    async def _query_anthropic(self, prompt: str) -> Optional[str]:
        """Query Anthropic model"""
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic query failed: {str(e)}")
            return None
    
    def _parse_ai_response(self, ai_response: str) -> Dict:
        """Parse AI response into structured format"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            
            if json_match:
                ai_data = json.loads(json_match.group())
                
                return {
                    "method": "ai_powered",
                    "risk_score": ai_data.get("risk_score", 50),
                    "risk_level": ai_data.get("risk_level", "medium"),
                    "key_risks": ai_data.get("key_risks", []),
                    "recommendations": ai_data.get("recommendations", []),
                    "confidence": ai_data.get("confidence", 0.7),
                    "reasoning": ai_data.get("reasoning", ""),
                    "raw_response": ai_response
                }
            else:
                # Fallback: parse text response
                return self._parse_text_response(ai_response)
                
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            return {
                "method": "ai_powered",
                "risk_score": 50,
                "risk_level": "medium",
                "confidence": 0.5,
                "error": str(e),
                "raw_response": ai_response
            }
    
    def _parse_text_response(self, response: str) -> Dict:
        """Parse text response when JSON parsing fails"""
        risk_level = "medium"
        risk_score = 50
        
        # Simple keyword-based parsing
        response_lower = response.lower()
        
        if "critical" in response_lower or "high risk" in response_lower:
            risk_level = "critical"
            risk_score = 80
        elif "high" in response_lower:
            risk_level = "high"
            risk_score = 70
        elif "low" in response_lower:
            risk_level = "low"
            risk_score = 30
        
        return {
            "method": "ai_powered",
            "risk_score": risk_score,
            "risk_level": risk_level,
            "confidence": 0.6,
            "raw_response": response
        }
    
    def _combine_assessments(self, rule_based: Dict, ai_powered: Dict) -> Dict:
        """Combine rule-based and AI-powered assessments"""
        combined = {
            "rule_based": rule_based,
            "ai_powered": ai_powered
        }
        
        # Calculate weighted combination
        rule_weight = 0.6  # Rule-based gets more weight due to higher confidence
        ai_weight = 0.4
        
        rule_score = rule_based.get("risk_score", 0)
        ai_score = ai_powered.get("risk_score", 0)
        
        # Only use AI score if it's available and confident
        if ai_powered.get("confidence", 0) > 0.6:
            combined_score = (rule_score * rule_weight) + (ai_score * ai_weight)
            combined_confidence = (rule_based.get("confidence", 0) + ai_powered.get("confidence", 0)) / 2
        else:
            combined_score = rule_score
            combined_confidence = rule_based.get("confidence", 0)
        
        combined_risk_level = self._calculate_risk_level(combined_score)
        
        return {
            "risk_score": combined_score,
            "risk_level": combined_risk_level,
            "confidence": combined_confidence,
            "risk_factors": rule_based.get("risk_factors", {}),
            "detailed_analysis": combined
        }
    
    def _calculate_risk_level(self, score: float) -> str:
        """Calculate risk level from score"""
        if score >= 80:
            return "critical"
        elif score >= 60:
            return "high"
        elif score >= 40:
            return "medium"
        else:
            return "low"
    
    async def _generate_recommendations(self, risk_assessment: Dict) -> List[str]:
        """Generate specific recommendations based on risk assessment"""
        recommendations = []
        
        risk_factors = risk_assessment.get("risk_factors", {})
        
        for factor_name, factor_data in risk_factors.items():
            score = factor_data.get("score", 0)
            
            if score > 60:  # High risk factor
                if factor_name == "security":
                    recommendations.append("Address security vulnerabilities immediately before deployment")
                    recommendations.append("Conduct security code review and penetration testing")
                elif factor_name == "performance":
                    recommendations.append("Optimize performance bottlenecks identified in the analysis")
                    recommendations.append("Consider load testing in staging environment")
                elif factor_name == "test_coverage":
                    recommendations.append("Increase test coverage to at least 80%")
                    recommendations.append("Add tests for critical business logic")
                elif factor_name == "test_failures":
                    recommendations.append("Fix all failing tests before deployment")
                    recommendations.append("Investigate root cause of test failures")
                elif factor_name == "complexity":
                    recommendations.append("Refactor complex code to improve maintainability")
                    recommendations.append("Add documentation for complex algorithms")
                elif factor_name == "quality":
                    recommendations.append("Address code quality issues flagged by static analysis")
                    recommendations.append("Consider pair programming for complex changes")
        
        # Add AI-powered recommendations if available
        ai_recommendations = risk_assessment.get("detailed_analysis", {}).get("ai_powered", {}).get("recommendations", [])
        recommendations.extend(ai_recommendations)
        
        # Add general recommendations based on risk level
        risk_level = risk_assessment.get("risk_level", "medium")
        
        if risk_level == "critical":
            recommendations.append("DO NOT DEPLOY - Critical issues must be resolved first")
            recommendations.append("Conduct thorough code review with senior developers")
            recommendations.append("Consider breaking changes into smaller, safer increments")
        elif risk_level == "high":
            recommendations.append("Requires additional review before deployment")
            recommendations.append("Deploy during low-traffic periods with rollback plan")
            recommendations.append("Monitor closely after deployment")
        elif risk_level == "medium":
            recommendations.append("Consider additional testing in staging environment")
            recommendations.append("Monitor key metrics after deployment")
        
        return list(set(recommendations))  # Remove duplicates
    
    def calculate_overall_risk(self, commit_results: List[Dict]) -> str:
        """Calculate overall risk for multiple commits"""
        if not commit_results:
            return "unknown"
        
        risk_scores = []
        for commit in commit_results:
            risk_assessment = commit.get("risk_assessment", {})
            risk_score = risk_assessment.get("risk_score", 0)
            risk_scores.append(risk_score)
        
        # Use the maximum risk score (most conservative approach)
        max_risk_score = max(risk_scores) if risk_scores else 0
        
        return self._calculate_risk_level(max_risk_score)
    
    def get_recommendation(self, risk_level: str) -> str:
        """Get recommendation based on risk level"""
        recommendations = {
            "low": "✅ Safe to merge - Low risk changes detected",
            "medium": "⚠️ Proceed with caution - Medium risk changes detected, consider additional review",
            "high": "🚨 High risk changes - Requires thorough review and testing before merge",
            "critical": "❌ DO NOT MERGE - Critical issues must be resolved first"
        }
        
        return recommendations.get(risk_level, "Unknown risk level")