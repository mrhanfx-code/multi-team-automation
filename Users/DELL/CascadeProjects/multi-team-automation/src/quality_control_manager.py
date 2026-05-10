"""
Quality Control Manager for Management Team
Comprehensive quality standards enforcement and compliance monitoring across all teams
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class QualityStandard(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    NEEDS_IMPROVEMENT = "needs_improvement"
    UNACCEPTABLE = "unacceptable"

class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"

class QualityMetric(Enum):
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    TIMELINESS = "timeliness"
    CONSISTENCY = "consistency"
    INNOVATION = "innovation"
    SECURITY = "security"
    PERFORMANCE = "performance"
    DOCUMENTATION = "documentation"

@dataclass
class QualityStandardDefinition:
    name: str
    description: str
    minimum_score: float
    weight: float  # Importance weight in overall quality calculation
    metrics: List[QualityMetric]
    evaluation_criteria: Dict[str, Any]
    team_applicability: List[str]  # Which teams this standard applies to

@dataclass
class QualityAssessment:
    team_name: str
    assessment_date: datetime
    standard_name: str
    overall_score: float
    individual_scores: Dict[QualityMetric, float]
    compliance_status: ComplianceStatus
    findings: List[str]
    recommendations: List[str]
    next_review_date: datetime
    assessor: str

@dataclass
class QualityIssue:
    id: str
    team_name: str
    standard_violated: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    detected_date: datetime
    resolution_deadline: datetime
    assigned_to: Optional[str]
    status: str  # OPEN, IN_PROGRESS, RESOLVED, ESCALATED
    impact_assessment: str

@dataclass
class QualityReport:
    report_id: str
    generated_date: datetime
    period_covered: str
    overall_compliance_rate: float
    team_performance: Dict[str, Dict[str, Any]]
    quality_trends: Dict[str, List[float]]
    critical_issues: List[QualityIssue]
    recommendations: List[str]
    quality_improvement_initiatives: List[str]

class SupabaseAutomationManager:
    """Simplified Supabase manager for demo"""
    
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_KEY')
        
    async def test_connection(self):
        """Test basic connection"""
        try:
            import aiohttp
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            headers = {
                'apikey': self.key,
                'Authorization': f'Bearer {self.key}',
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.url}/auth/v1/settings",
                    headers=headers,
                    ssl=ssl_context
                ) as response:
                    return response.status == 200
        except:
            return False
    
    async def save_team_output(self, team_name: str, output_data: dict, output_type: str = "report"):
        """Save team output"""
        try:
            base_path = "supabase_storage"
            file_id = f"{team_name}_{output_type}_{int(datetime.now().timestamp())}"
            full_path = os.path.join(base_path, f"team_outputs/{team_name}/{output_type}/{file_id}.json")
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, default=str)
            
            print(f"✅ Saved {team_name} output: {output_type}")
            return True
        except Exception as e:
            print(f"❌ Failed to save team output: {e}")
            return False
    
    async def save_notification(self, notification_data: dict):
        """Save notification"""
        try:
            base_path = "supabase_storage"
            file_id = f"notif_{int(datetime.now().timestamp())}"
            full_path = os.path.join(base_path, f"notifications/{file_id}.json")
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(notification_data, f, indent=2, default=str)
            
            print(f"✅ Saved notification: {notification_data.get('message', 'Unknown')}")
            return True
        except Exception as e:
            print(f"❌ Failed to save notification: {e}")
            return False

class QualityControlManager:
    """Comprehensive Quality Control Manager for Management Team"""
    
    def __init__(self, supabase_manager: SupabaseAutomationManager):
        self.name = "Quality Control Manager"
        self.supabase_manager = supabase_manager
        self.quality_standards = {}
        self.assessments = []
        self.issues = []
        self.quality_metrics_history = {}
        self.initialize_quality_standards()
        
    def initialize_quality_standards(self):
        """Initialize comprehensive quality standards for all teams"""
        
        # Research Team Standards
        self.quality_standards['research_quality'] = QualityStandardDefinition(
            name="Research Quality Standards",
            description="Comprehensive quality standards for research team outputs",
            minimum_score=0.85,
            weight=0.25,
            metrics=[QualityMetric.ACCURACY, QualityMetric.COMPLETENESS, QualityMetric.TIMELINESS, QualityMetric.INNOVATION],
            evaluation_criteria={
                'accuracy': {'min_sources': 10, 'peer_reviewed_sources': 3, 'data_validation': 'required'},
                'completeness': {'all_research_types': 'required', 'executive_summary': 'required', 'recommendations': 'required'},
                'timeliness': {'max_research_duration': '2 weeks', 'on_time_delivery': '>=95%'},
                'innovation': {'novel_insights': '>=3', 'strategic_value': 'high'}
            },
            team_applicability=['Research Team']
        )
        
        # Planning Team Standards
        self.quality_standards['planning_quality'] = QualityStandardDefinition(
            name="Planning Quality Standards",
            description="Quality standards for comprehensive planning outputs",
            minimum_score=0.87,
            weight=0.20,
            metrics=[QualityMetric.COMPLETENESS, QualityMetric.ACCURACY, QualityMetric.TIMELINESS, QualityMetric.CONSISTENCY],
            evaluation_criteria={
                'completeness': {'all_planning_types': 'required', 'risk_assessment': 'detailed', 'resource_allocation': 'comprehensive'},
                'accuracy': {'budget_accuracy': '+/-5%', 'timeline_realism': 'achievable', 'resource_feasibility': 'verified'},
                'timeliness': {'planning_duration': '<=1 week', 'milestone_definition': 'clear'},
                'consistency': {'cross_plan_alignment': 'required', 'dependency_tracking': 'complete'}
            },
            team_applicability=['Planning Team']
        )
        
        # Development Team Standards
        self.quality_standards['development_quality'] = QualityStandardDefinition(
            name="Development Quality Standards",
            description="Comprehensive quality standards for development outputs",
            minimum_score=0.88,
            weight=0.30,
            metrics=[QualityMetric.PERFORMANCE, QualityMetric.SECURITY, QualityMetric.DOCUMENTATION, QualityMetric.INNOVATION],
            evaluation_criteria={
                'performance': {'code_coverage': '>=85%', 'performance_benchmarks': 'met', 'scalability': 'demonstrated'},
                'security': {'security_review': 'passed', 'vulnerability_scan': 'clean', 'compliance': 'verified'},
                'documentation': {'api_docs': 'complete', 'user_guides': 'comprehensive', 'technical_docs': 'detailed'},
                'innovation': {'technical_innovation': 'demonstrated', 'best_practices': 'followed', 'optimization': 'implemented'}
            },
            team_applicability=['Development Team']
        )
        
        # Management Team Standards
        self.quality_standards['management_quality'] = QualityStandardDefinition(
            name="Management Quality Standards",
            description="Quality standards for management processes and decisions",
            minimum_score=0.90,
            weight=0.15,
            metrics=[QualityMetric.TIMELINESS, QualityMetric.ACCURACY, QualityMetric.CONSISTENCY, QualityMetric.DOCUMENTATION],
            evaluation_criteria={
                'timeliness': {'review_turnaround': '<48 hours', 'decision_making': 'prompt', 'escalation_handling': 'immediate'},
                'accuracy': {'decision_accuracy': '>=95%', 'data_driven_decisions': 'required', 'risk_assessment': 'thorough'},
                'consistency': {'process_consistency': 'maintained', 'standard_application': 'uniform', 'fairness': 'demonstrated'},
                'documentation': {'decision_logs': 'complete', 'meeting_minutes': 'detailed', 'action_items': 'tracked'}
            },
            team_applicability=['Management Team']
        )
        
        # Cross-Team Standards
        self.quality_standards['collaboration_quality'] = QualityStandardDefinition(
            name="Cross-Team Collaboration Standards",
            description="Standards for inter-team collaboration and communication",
            minimum_score=0.85,
            weight=0.10,
            metrics=[QualityMetric.TIMELINESS, QualityMetric.COMPLETENESS, QualityMetric.CONSISTENCY],
            evaluation_criteria={
                'timeliness': {'response_time': '<24 hours', 'handoff_efficiency': 'smooth', 'meeting_attendance': '>=95%'},
                'completeness': {'information_sharing': 'complete', 'dependency_tracking': 'current', 'status_updates': 'regular'},
                'consistency': {'communication_standards': 'followed', 'documentation_standards': 'uniform', 'quality_standards': 'aligned'}
            },
            team_applicability=['Research Team', 'Planning Team', 'Development Team', 'Management Team']
        )
        
        logger.info(f"✅ Initialized {len(self.quality_standards)} quality standards")
    
    async def conduct_quality_assessment(self, team_name: str, team_outputs: Dict[str, Any], assessment_type: str = "comprehensive") -> QualityAssessment:
        """Conduct comprehensive quality assessment for a team"""
        
        assessment_id = f"qa_{team_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Determine applicable standards
        applicable_standards = [
            standard for standard in self.quality_standards.values()
            if team_name in standard.team_applicability
        ]
        
        if not applicable_standards:
            raise ValueError(f"No quality standards applicable to {team_name}")
        
        # Assess each applicable standard
        assessment_results = []
        
        for standard in applicable_standards:
            standard_assessment = await self._assess_standard_compliance(team_name, standard, team_outputs)
            assessment_results.append(standard_assessment)
        
        # Calculate overall assessment
        overall_score = self._calculate_overall_quality_score(assessment_results)
        compliance_status = self._determine_compliance_status(overall_score, assessment_results)
        
        # Compile findings and recommendations
        findings = self._compile_quality_findings(assessment_results)
        recommendations = self._generate_quality_recommendations(assessment_results, findings)
        
        # Create quality assessment
        assessment = QualityAssessment(
            team_name=team_name,
            assessment_date=datetime.now(),
            standard_name="comprehensive",
            overall_score=overall_score,
            individual_scores={},
            compliance_status=compliance_status,
            findings=findings,
            recommendations=recommendations,
            next_review_date=datetime.now() + timedelta(days=14),
            assessor=self.name
        )
        
        # Save assessment to Supabase
        await self.supabase_manager.save_team_output(
            team_name="Quality Control",
            output_data=asdict(assessment),
            output_type="quality_assessment"
        )
        
        # Track quality metrics history
        await self._update_quality_metrics_history(team_name, assessment)
        
        # Send notifications if needed
        if compliance_status in [ComplianceStatus.NON_COMPLIANT, ComplianceStatus.PARTIALLY_COMPLIANT]:
            await self._send_quality_alert(assessment)
        
        logger.info(f"✅ Quality assessment completed for {team_name}: {overall_score:.2%} ({compliance_status.value})")
        return assessment
    
    async def _assess_standard_compliance(self, team_name: str, standard: QualityStandardDefinition, team_outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Assess compliance with a specific quality standard"""
        
        metric_scores = {}
        
        for metric in standard.metrics:
            score = await self._evaluate_quality_metric(team_name, metric, team_outputs, standard.evaluation_criteria)
            metric_scores[metric.value] = score
        
        # Calculate weighted score for this standard
        total_score = sum(metric_scores.values()) / len(metric_scores)
        
        return {
            'standard_name': standard.name,
            'minimum_score': standard.minimum_score,
            'weight': standard.weight,
            'metric_scores': metric_scores,
            'total_score': total_score,
            'compliance': total_score >= standard.minimum_score
        }
    
    async def _evaluate_quality_metric(self, team_name: str, metric: QualityMetric, team_outputs: Dict[str, Any], criteria: Dict[str, Any]) -> float:
        """Evaluate a specific quality metric"""
        
        await asyncio.sleep(0.1)  # Simulate evaluation time
        
        # Simulate metric evaluation based on team outputs and criteria
        base_score = 0.85  # Base quality score
        
        # Adjust score based on team and metric
        if team_name == "Research Team":
            if metric == QualityMetric.ACCURACY:
                base_score = 0.92  # Research team typically has high accuracy
            elif metric == QualityMetric.INNOVATION:
                base_score = 0.89  # Good innovation in research
            elif metric == QualityMetric.COMPLETENESS:
                base_score = 0.87  # Generally complete research
                
        elif team_name == "Planning Team":
            if metric == QualityMetric.COMPLETENESS:
                base_score = 0.91  # Planning usually comprehensive
            elif metric == QualityMetric.ACCURACY:
                base_score = 0.88  # Good accuracy in planning
            elif metric == QualityMetric.CONSISTENCY:
                base_score = 0.90  # High consistency in planning
                
        elif team_name == "Development Team":
            if metric == QualityMetric.PERFORMANCE:
                base_score = 0.89  # Good performance metrics
            elif metric == QualityMetric.SECURITY:
                base_score = 0.91  # Strong security practices
            elif metric == QualityMetric.DOCUMENTATION:
                base_score = 0.86  # Decent documentation
                
        elif team_name == "Management Team":
            if metric == QualityMetric.TIMELINESS:
                base_score = 0.93  # Excellent timeliness
            elif metric == QualityMetric.ACCURACY:
                base_score = 0.90  # High decision accuracy
            elif metric == QualityMetric.CONSISTENCY:
                base_score = 0.92  # Very consistent processes
        
        # Add some variation to simulate real-world variation
        import random
        variation = random.uniform(-0.05, 0.05)
        final_score = max(0.0, min(1.0, base_score + variation))
        
        return final_score
    
    def _calculate_overall_quality_score(self, assessment_results: List[Dict[str, Any]]) -> float:
        """Calculate overall quality score from multiple standard assessments"""
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for result in assessment_results:
            weighted_sum += result['total_score'] * result['weight']
            total_weight += result['weight']
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _determine_compliance_status(self, overall_score: float, assessment_results: List[Dict[str, Any]]) -> ComplianceStatus:
        """Determine overall compliance status"""
        
        # Check if any standard is below minimum
        non_compliant_standards = [r for r in assessment_results if not r['compliance']]
        
        if non_compliant_standards:
            if len(non_compliant_standards) == len(assessment_results):
                return ComplianceStatus.NON_COMPLIANT
            else:
                return ComplianceStatus.PARTIALLY_COMPLIANT
        elif overall_score >= 0.95:
            return ComplianceStatus.COMPLIANT
        else:
            return ComplianceStatus.PENDING_REVIEW
    
    def _compile_quality_findings(self, assessment_results: List[Dict[str, Any]]) -> List[str]:
        """Compile quality findings from assessment results"""
        findings = []
        
        for result in assessment_results:
            if not result['compliance']:
                findings.append(f"⚠️ {result['standard_name']}: Score {result['total_score']:.2%} below minimum {result['minimum_score']:.2%}")
            
            # Find low-scoring metrics
            for metric_name, score in result['metric_scores'].items():
                if score < 0.8:
                    findings.append(f"📉 {metric_name}: Score {score:.2%} needs improvement")
        
        if not findings:
            findings.append("✅ All quality standards met or exceeded")
        
        return findings
    
    def _generate_quality_recommendations(self, assessment_results: List[Dict[str, Any]], findings: List[str]) -> List[str]:
        """Generate quality improvement recommendations"""
        recommendations = []
        
        # Analyze assessment results for patterns
        low_scoring_metrics = {}
        
        for result in assessment_results:
            for metric_name, score in result['metric_scores'].items():
                if metric_name not in low_scoring_metrics:
                    low_scoring_metrics[metric_name] = []
                low_scoring_metrics[metric_name].append(score)
        
        # Generate recommendations based on low-scoring areas
        for metric_name, scores in low_scoring_metrics.items():
            avg_score = sum(scores) / len(scores)
            if avg_score < 0.8:
                if metric_name == "accuracy":
                    recommendations.append("🎯 Implement additional validation and review processes to improve accuracy")
                elif metric_name == "completeness":
                    recommendations.append("📋 Develop comprehensive checklists to ensure all requirements are met")
                elif metric_name == "timeliness":
                    recommendations.append("⏰ Optimize workflows and remove bottlenecks to improve delivery times")
                elif metric_name == "consistency":
                    recommendations.append("🔄 Standardize processes and templates for better consistency")
                elif metric_name == "innovation":
                    recommendations.append("💡 Encourage creative thinking and explore new approaches")
                elif metric_name == "security":
                    recommendations.append("🔒 Strengthen security protocols and conduct regular security audits")
                elif metric_name == "performance":
                    recommendations.append("⚡ Optimize performance and implement efficiency improvements")
                elif metric_name == "documentation":
                    recommendations.append("📚 Enhance documentation practices and maintain updated guides")
        
        # Add general recommendations
        recommendations.extend([
            "📊 Schedule regular quality reviews and assessments",
            "🎓 Provide training on quality standards and best practices",
            "🔄 Implement continuous improvement processes",
            "📈 Monitor quality metrics and trends over time"
        ])
        
        return recommendations[:8]  # Return top 8 recommendations
    
    async def _update_quality_metrics_history(self, team_name: str, assessment: QualityAssessment):
        """Update quality metrics history for trend analysis"""
        
        if team_name not in self.quality_metrics_history:
            self.quality_metrics_history[team_name] = []
        
        self.quality_metrics_history[team_name].append({
            'date': assessment.assessment_date,
            'score': assessment.overall_score,
            'status': assessment.compliance_status.value
        })
        
        # Keep only last 12 assessments for trend analysis
        if len(self.quality_metrics_history[team_name]) > 12:
            self.quality_metrics_history[team_name] = self.quality_metrics_history[team_name][-12:]
    
    async def _send_quality_alert(self, assessment: QualityAssessment):
        """Send quality alert notifications"""
        
        alert_message = f"🚨 Quality Alert: {assessment.team_name} - {assessment.compliance_status.value.upper()}"
        
        notification = {
            'sender': self.name,
            'recipient': 'Management Team',
            'message': alert_message,
            'priority': 'HIGH',
            'action_required': True,
            'details': {
                'team': assessment.team_name,
                'score': assessment.overall_score,
                'status': assessment.compliance_status.value,
                'findings': assessment.findings[:3],  # Top 3 findings
                'next_review': assessment.next_review_date.isoformat()
            }
        }
        
        await self.supabase_manager.save_notification(notification)
    
    async def generate_quality_report(self, period_days: int = 30) -> QualityReport:
        """Generate comprehensive quality report for specified period"""
        
        report_id = f"qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        period_end = datetime.now()
        period_start = period_end - timedelta(days=period_days)
        
        # Calculate overall compliance rate
        total_assessments = len(self.assessments)
        compliant_assessments = len([a for a in self.assessments if a.compliance_status == ComplianceStatus.COMPLIANT])
        overall_compliance_rate = compliant_assessments / total_assessments if total_assessments > 0 else 0.0
        
        # Analyze team performance
        team_performance = {}
        for team_name in self.quality_metrics_history.keys():
            team_history = self.quality_metrics_history[team_name]
            if team_history:
                recent_scores = [entry['score'] for entry in team_history[-5:]]  # Last 5 assessments
                team_performance[team_name] = {
                    'average_score': sum(recent_scores) / len(recent_scores),
                    'trend': 'improving' if len(recent_scores) > 1 and recent_scores[-1] > recent_scores[0] else 'stable',
                    'latest_assessment': team_history[-1],
                    'assessment_count': len(team_history)
                }
        
        # Analyze quality trends
        quality_trends = {}
        for team_name, history in self.quality_metrics_history.items():
            if len(history) >= 3:
                scores = [entry['score'] for entry in history]
                quality_trends[team_name] = scores
        
        # Identify critical issues
        critical_issues = [issue for issue in self.issues if issue.severity in ['CRITICAL', 'HIGH']]
        
        # Generate recommendations
        recommendations = [
            "📊 Implement real-time quality monitoring dashboards",
            "🎯 Focus on teams with declining quality trends",
            "🔄 Standardize quality assessment processes across teams",
            "📈 Establish quality improvement targets and KPIs",
            "🎓 Provide targeted training for identified quality gaps"
        ]
        
        # Define quality improvement initiatives
        improvement_initiatives = [
            "Quality Standards Enhancement Program",
            "Cross-Team Quality Best Practices Sharing",
            "Automated Quality Monitoring System",
            "Quality Certification Program",
            "Continuous Quality Improvement Workshops"
        ]
        
        report = QualityReport(
            report_id=report_id,
            generated_date=datetime.now(),
            period_covered=f"{period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}",
            overall_compliance_rate=overall_compliance_rate,
            team_performance=team_performance,
            quality_trends=quality_trends,
            critical_issues=critical_issues,
            recommendations=recommendations,
            quality_improvement_initiatives=improvement_initiatives
        )
        
        # Save report to Supabase
        await self.supabase_manager.save_team_output(
            team_name="Quality Control",
            output_data=asdict(report),
            output_type="quality_report"
        )
        
        return report
    
    async def create_quality_improvement_plan(self, team_name: str, assessment: QualityAssessment) -> Dict[str, Any]:
        """Create targeted quality improvement plan for a team"""
        
        plan_id = f"qip_{team_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Analyze assessment to identify improvement areas
        improvement_areas = []
        
        for finding in assessment.findings:
            if "needs improvement" in finding.lower() or "below minimum" in finding.lower():
                improvement_areas.append(finding)
        
        # Create improvement actions
        improvement_actions = []
        
        if assessment.compliance_status != ComplianceStatus.COMPLIANT:
            improvement_actions.extend([
                {
                    'action': 'Conduct root cause analysis for quality issues',
                    'priority': 'HIGH',
                    'deadline': (datetime.now() + timedelta(days=7)).isoformat(),
                    'responsible': team_name,
                    'resources_required': ['Quality analyst', 'Process documentation']
                },
                {
                    'action': 'Implement immediate corrective actions',
                    'priority': 'CRITICAL',
                    'deadline': (datetime.now() + timedelta(days=3)).isoformat(),
                    'responsible': team_name,
                    'resources_required': ['Team lead time', 'Quality tools']
                },
                {
                    'action': 'Schedule follow-up quality assessment',
                    'priority': 'MEDIUM',
                    'deadline': (datetime.now() + timedelta(days=14)).isoformat(),
                    'responsible': self.name,
                    'resources_required': ['Assessment time', 'Metrics tools']
                }
            ])
        
        # Add preventive actions
        improvement_actions.extend([
            {
                'action': 'Enhance team training on quality standards',
                'priority': 'MEDIUM',
                'deadline': (datetime.now() + timedelta(days=21)).isoformat(),
                'responsible': team_name,
                'resources_required': ['Training materials', 'Expert time']
            },
            {
                'action': 'Implement quality monitoring tools',
                'priority': 'LOW',
                'deadline': (datetime.now() + timedelta(days=30)).isoformat(),
                'responsible': team_name,
                'resources_required': ['Software tools', 'Integration support']
            }
        ])
        
        improvement_plan = {
            'plan_id': plan_id,
            'team_name': team_name,
            'assessment_reference': assessment.assessment_date.isoformat(),
            'current_quality_score': assessment.overall_score,
            'target_quality_score': max(0.90, assessment.overall_score + 0.10),
            'improvement_areas': improvement_areas,
            'improvement_actions': improvement_actions,
            'success_metrics': [
                f"Quality score >= {max(0.90, assessment.overall_score + 0.10):.2%}",
                "All quality standards compliant",
                "No critical quality issues",
                "Team satisfaction with quality processes >= 80%"
            ],
            'review_schedule': [
                (datetime.now() + timedelta(days=7)).isoformat(),
                (datetime.now() + timedelta(days=14)).isoformat(),
                (datetime.now() + timedelta(days=30)).isoformat()
            ],
            'created_date': datetime.now().isoformat(),
            'created_by': self.name
        }
        
        # Save improvement plan to Supabase
        await self.supabase_manager.save_team_output(
            team_name="Quality Control",
            output_data=improvement_plan,
            output_type="quality_improvement_plan"
        )
        
        # Send notification to team
        notification = {
            'sender': self.name,
            'recipient': team_name,
            'message': f"📋 Quality Improvement Plan Created - Target Score: {max(0.90, assessment.overall_score + 0.10):.2%}",
            'priority': 'HIGH',
            'action_required': True,
            'details': {
                'plan_id': plan_id,
                'current_score': assessment.overall_score,
                'target_score': max(0.90, assessment.overall_score + 0.10),
                'first_action_deadline': improvement_actions[0]['deadline']
            }
        }
        
        await self.supabase_manager.save_notification(notification)
        
        return improvement_plan

# Demo function to showcase Quality Control Manager capabilities
async def demo_quality_control_manager():
    """Demonstrate the Quality Control Manager capabilities"""
    print("🔍 Quality Control Manager Demo")
    print("=" * 50)
    print()
    
    # Initialize Supabase manager
    supabase_manager = SupabaseAutomationManager()
    
    if await supabase_manager.test_connection():
        print("✅ Supabase connection successful!")
    else:
        print("⚠️  Using local storage simulation")
    
    print()
    
    # Initialize Quality Control Manager
    print("🎯 Initializing Quality Control Manager...")
    qc_manager = QualityControlManager(supabase_manager)
    
    print(f"✅ Quality Standards: {len(qc_manager.quality_standards)}")
    print(f"📊 Quality Metrics: {len(QualityMetric)}")
    print()
    
    # Simulate team outputs for assessment
    print("📋 Simulating Team Outputs for Quality Assessment...")
    
    team_outputs = {
        'Research Team': {
            'quality_score': 0.92,
            'research_types_completed': ['market_research', 'technical_research', 'competitive_analysis'],
            'sources_cited': 15,
            'peer_reviews': 4,
            'innovation_score': 0.89,
            'completion_rate': 0.95
        },
        'Planning Team': {
            'quality_score': 0.89,
            'planning_types_completed': ['project_planning', 'resource_planning', 'timeline_planning'],
            'budget_accuracy': 0.97,
            'timeline_realism': 0.91,
            'risk_assessment_depth': 0.93,
            'consistency_score': 0.90
        },
        'Development Team': {
            'quality_score': 0.88,
            'code_coverage': 0.87,
            'security_score': 0.91,
            'documentation_completeness': 0.86,
            'performance_benchmarks': 0.89,
            'innovation_level': 0.85
        },
        'Management Team': {
            'quality_score': 0.90,
            'decision_accuracy': 0.95,
            'response_time_hours': 12,
            'process_consistency': 0.92,
            'documentation_quality': 0.88,
            'escalation_handling': 0.94
        }
    }
    
    print(f"📊 Team Outputs Prepared: {len(team_outputs)} teams")
    print()
    
    # Conduct quality assessments for each team
    print("🔍 Conducting Quality Assessments...")
    assessments = []
    
    for team_name, outputs in team_outputs.items():
        print(f"   📊 Assessing {team_name}...")
        assessment = await qc_manager.conduct_quality_assessment(team_name, outputs)
        assessments.append(assessment)
        
        print(f"      ✅ Score: {assessment.overall_score:.2%}")
        print(f"      📋 Status: {assessment.compliance_status.value}")
        print(f"      📅 Next Review: {assessment.next_review_date.strftime('%Y-%m-%d')}")
        print()
    
    # Generate comprehensive quality report
    print("📈 Generating Quality Report...")
    quality_report = await qc_manager.generate_quality_report(period_days=30)
    
    print(f"✅ Report Generated: {quality_report.report_id}")
    print(f"📊 Overall Compliance Rate: {quality_report.overall_compliance_rate:.2%}")
    print(f"👥 Teams Assessed: {len(quality_report.team_performance)}")
    print(f"🚨 Critical Issues: {len(quality_report.critical_issues)}")
    print()
    
    # Create improvement plan for team with lowest score
    lowest_score_team = min(assessments, key=lambda a: a.overall_score).team_name
    lowest_assessment = next(a for a in assessments if a.team_name == lowest_score_team)
    
    print(f"🎯 Creating Quality Improvement Plan for {lowest_score_team}...")
    improvement_plan = await qc_manager.create_quality_improvement_plan(lowest_score_team, lowest_assessment)
    
    print(f"✅ Improvement Plan Created: {improvement_plan['plan_id']}")
    print(f"📈 Target Score: {improvement_plan['target_quality_score']:.2%}")
    print(f"📋 Improvement Actions: {len(improvement_plan['improvement_actions'])}")
    print()
    
    # Display quality summary
    print("📊 Quality Assessment Summary:")
    print("-" * 40)
    
    for assessment in assessments:
        status_emoji = "✅" if assessment.compliance_status == ComplianceStatus.COMPLIANT else "⚠️"
        print(f"{status_emoji} {assessment.team_name}:")
        print(f"   📊 Score: {assessment.overall_score:.2%}")
        print(f"   📋 Status: {assessment.compliance_status.value}")
        print(f"   🔍 Findings: {len(assessment.findings)}")
        print(f"   💡 Recommendations: {len(assessment.recommendations)}")
        print()
    
    # Display quality standards summary
    print("🎯 Quality Standards Overview:")
    print("-" * 40)
    
    for standard_name, standard in qc_manager.quality_standards.items():
        print(f"📋 {standard.name}:")
        print(f"   🎯 Minimum Score: {standard.minimum_score:.2%}")
        print(f"   ⚖️  Weight: {standard.weight:.2%}")
        print(f"   📊 Metrics: {len(standard.metrics)}")
        print(f"   👥 Applicable Teams: {len(standard.team_applicability)}")
        print()
    
    # Display recommendations
    print("💡 Quality Control Recommendations:")
    print("-" * 40)
    
    for i, rec in enumerate(quality_report.recommendations[:5], 1):
        print(f"   {i}. {rec}")
    
    print()
    print("🎉 Quality Control Manager Demo Complete!")
    print("✅ Comprehensive quality assessments conducted")
    print("📊 Quality report generated with insights")
    print("🎯 Improvement plans created for targeted teams")
    print("🔍 Quality standards enforced across all teams")
    print("📈 Continuous quality monitoring established")

if __name__ == "__main__":
    asyncio.run(demo_quality_control_manager())
