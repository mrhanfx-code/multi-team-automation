#!/usr/bin/env python3
"""
MFM Corporation - Operations Manager
Ensures all agents are working and there is no idle agents with current skills and setup
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json

logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"

class AgentType(Enum):
    RESEARCH = "research"
    PLANNING = "planning"
    DEVELOPMENT = "development"
    MANAGEMENT = "management"
    INNOVATION = "innovation"
    MARKETING = "marketing"
    MEDIA = "media"
    TECHNOLOGY = "technology"
    MCP_LLM = "mcp_llm"
    MARKET_INTELLIGENCE = "market_intelligence"
    LEGAL = "legal"
    GENERAL_MANAGER = "general_manager"

class OptimizationAction(Enum):
    REDISTRIBUTE_WORKLOAD = "redistribute_workload"
    SCALE_RESOURCES = "scale_resources"
    UPDATE_SKILLS = "update_skills"
    MAINTENANCE_SCHEDULE = "maintenance_schedule"
    PERFORMANCE_TUNING = "performance_tuning"
    WORKFLOW_OPTIMIZATION = "workflow_optimization"

@dataclass
class AgentMetrics:
    """Agent performance metrics"""
    agent_id: str
    agent_type: AgentType
    status: AgentStatus
    current_task: Optional[str]
    tasks_completed: int
    tasks_failed: int
    average_task_time: float
    utilization_rate: float
    performance_score: float
    last_active: datetime
    skills: List[str]
    capacity: int
    current_load: int
    error_rate: float
    response_time_ms: float

@dataclass
class WorkloadDistribution:
    """Workload distribution across agents"""
    total_tasks: int
    distributed_tasks: int
    pending_tasks: int
    agent_loads: Dict[str, int]
    bottlenecks: List[str]
    underutilized_agents: List[str]
    optimal_distribution: Dict[str, int]

@dataclass
class OptimizationRecommendation:
    """Optimization recommendation"""
    id: str
    action: OptimizationAction
    priority: str
    description: str
    target_agents: List[str]
    expected_improvement: str
    implementation_steps: List[str]
    estimated_time: timedelta
    created_at: datetime

class OperationsManager:
    """Operations Manager for agent monitoring and optimization"""
    
    def __init__(self, supabase_manager):
        self.supabase_manager = supabase_manager
        self.agent_metrics = {}
        self.workload_distribution = None
        self.optimization_recommendations = {}
        self.monitoring_active = True
        self.optimization_enabled = True
        
        # Performance thresholds
        self.idle_threshold = 0.1  # 10% utilization considered idle
        self.overload_threshold = 0.9  # 90% utilization considered overloaded
        self.performance_threshold = 0.7  # 70% performance score minimum
        self.error_rate_threshold = 0.05  # 5% error rate maximum
        
    async def initialize(self) -> bool:
        """Initialize the Operations Manager"""
        logger.info("🔧 Initializing MFM Corporation Operations Manager")
        
        try:
            # Load agent metrics
            await self._load_agent_metrics()
            
            # Initialize monitoring
            await self._initialize_monitoring()
            
            # Set up optimization engine
            await self._setup_optimization_engine()
            
            logger.info("✅ Operations Manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Operations Manager initialization failed: {e}")
            return False
    
    async def monitor_all_agents(self) -> Dict[str, Any]:
        """Monitor all agents in the system"""
        try:
            logger.info("🔍 Monitoring all agents")
            
            monitoring_results = {
                "total_agents": len(self.agent_metrics),
                "active_agents": 0,
                "idle_agents": 0,
                "busy_agents": 0,
                "offline_agents": 0,
                "error_agents": 0,
                "average_utilization": 0.0,
                "average_performance": 0.0,
                "system_health": "healthy",
                "issues": [],
                "recommendations": []
            }
            
            total_utilization = 0.0
            total_performance = 0.0
            
            for agent_id, metrics in self.agent_metrics.items():
                # Count agents by status
                if metrics.status == AgentStatus.ACTIVE:
                    monitoring_results["active_agents"] += 1
                elif metrics.status == AgentStatus.IDLE:
                    monitoring_results["idle_agents"] += 1
                elif metrics.status == AgentStatus.BUSY:
                    monitoring_results["busy_agents"] += 1
                elif metrics.status == AgentStatus.OFFLINE:
                    monitoring_results["offline_agents"] += 1
                elif metrics.status == AgentStatus.ERROR:
                    monitoring_results["error_agents"] += 1
                
                # Calculate averages
                total_utilization += metrics.utilization_rate
                total_performance += metrics.performance_score
                
                # Check for issues
                if metrics.utilization_rate < self.idle_threshold:
                    monitoring_results["issues"].append(f"Agent {agent_id} is idle ({metrics.utilization_rate:.1%} utilization)")
                
                if metrics.performance_score < self.performance_threshold:
                    monitoring_results["issues"].append(f"Agent {agent_id} has low performance ({metrics.performance_score:.1%})")
                
                if metrics.error_rate > self.error_rate_threshold:
                    monitoring_results["issues"].append(f"Agent {agent_id} has high error rate ({metrics.error_rate:.1%})")
            
            # Calculate averages
            if self.agent_metrics:
                monitoring_results["average_utilization"] = total_utilization / len(self.agent_metrics)
                monitoring_results["average_performance"] = total_performance / len(self.agent_metrics)
            
            # Determine system health
            if monitoring_results["error_agents"] > 0:
                monitoring_results["system_health"] = "critical"
            elif monitoring_results["idle_agents"] > len(self.agent_metrics) * 0.3:
                monitoring_results["system_health"] = "warning"
            elif monitoring_results["average_performance"] < self.performance_threshold:
                monitoring_results["system_health"] = "degraded"
            
            # Generate recommendations
            monitoring_results["recommendations"] = await self._generate_monitoring_recommendations(monitoring_results)
            
            logger.info(f"✅ Agent monitoring completed: {monitoring_results['system_health']} system health")
            return monitoring_results
            
        except Exception as e:
            logger.error(f"❌ Agent monitoring failed: {e}")
            return {}
    
    async def optimize_agent_allocation(self) -> Dict[str, Any]:
        """Optimize agent allocation and workload distribution"""
        try:
            logger.info("⚡ Optimizing agent allocation")
            
            optimization_results = {
                "current_distribution": {},
                "optimal_distribution": {},
                "improvements": [],
                "actions_taken": [],
                "expected_efficiency_gain": 0.0,
                "optimization_time": datetime.now().isoformat()
            }
            
            # Analyze current workload distribution
            current_distribution = await self._analyze_workload_distribution()
            optimization_results["current_distribution"] = current_distribution
            
            # Identify optimization opportunities
            opportunities = await self._identify_optimization_opportunities(current_distribution)
            
            # Generate optimization plan
            optimization_plan = await self._generate_optimization_plan(opportunities)
            
            # Implement optimizations
            implemented_actions = await self._implement_optimizations(optimization_plan)
            optimization_results["actions_taken"] = implemented_actions
            
            # Calculate expected improvements
            efficiency_gain = await self._calculate_efficiency_gain(current_distribution, optimization_plan)
            optimization_results["expected_efficiency_gain"] = efficiency_gain
            
            # Generate optimal distribution
            optimal_distribution = await self._generate_optimal_distribution(optimization_plan)
            optimization_results["optimal_distribution"] = optimal_distribution
            
            logger.info(f"✅ Agent allocation optimization completed: {efficiency_gain:.1%} expected efficiency gain")
            return optimization_results
            
        except Exception as e:
            logger.error(f"❌ Agent allocation optimization failed: {e}")
            return {}
    
    async def eliminate_idle_agents(self) -> Dict[str, Any]:
        """Eliminate idle agents by redistributing work"""
        try:
            logger.info("🎯 Eliminating idle agents")
            
            elimination_results = {
                "idle_agents_identified": [],
                "work_redistributed": [],
                "agents_reactivated": [],
                "new_tasks_assigned": 0,
                "utilization_improvement": 0.0,
                "elimination_time": datetime.now().isoformat()
            }
            
            # Identify idle agents
            idle_agents = []
            for agent_id, metrics in self.agent_metrics.items():
                if metrics.status == AgentStatus.IDLE and metrics.utilization_rate < self.idle_threshold:
                    idle_agents.append({
                        "agent_id": agent_id,
                        "agent_type": metrics.agent_type,
                        "current_load": metrics.current_load,
                        "capacity": metrics.capacity,
                        "skills": metrics.skills
                    })
            
            elimination_results["idle_agents_identified"] = idle_agents
            
            if not idle_agents:
                logger.info("✅ No idle agents found - all agents are properly utilized")
                return elimination_results
            
            # Find available work for idle agents
            available_work = await self._find_available_work(idle_agents)
            
            # Redistribute work to idle agents
            for idle_agent in idle_agents:
                agent_id = idle_agent["agent_id"]
                agent_type = idle_agent["agent_type"]
                
                # Find suitable work for this agent
                suitable_work = await self._find_suitable_work(agent_type, idle_agent["skills"], available_work)
                
                if suitable_work:
                    # Assign work to idle agent
                    await self._assign_work_to_agent(agent_id, suitable_work)
                    elimination_results["work_redistributed"].append({
                        "agent_id": agent_id,
                        "task_id": suitable_work["task_id"],
                        "task_type": suitable_work["task_type"]
                    })
                    
                    # Update agent status
                    await self._update_agent_status(agent_id, AgentStatus.BUSY)
                    elimination_results["agents_reactivated"].append(agent_id)
                    elimination_results["new_tasks_assigned"] += 1
            
            # Calculate utilization improvement
            if self.agent_metrics:
                old_utilization = sum(m.utilization_rate for m in self.agent_metrics.values()) / len(self.agent_metrics)
                new_utilization = old_utilization + (len(elimination_results["agents_reactivated"]) * 0.2)  # Estimate 20% improvement per reactivated agent
                elimination_results["utilization_improvement"] = min(new_utilization - old_utilization, 0.5)  # Cap at 50%
            
            logger.info(f"✅ Idle agent elimination completed: {len(elimination_results['agents_reactivated'])} agents reactivated")
            return elimination_results
            
        except Exception as e:
            logger.error(f"❌ Idle agent elimination failed: {e}")
            return {}
    
    async def ensure_agent_skills_match_workload(self) -> Dict[str, Any]:
        """Ensure agent skills match current workload requirements"""
        try:
            logger.info("🎓 Ensuring agent skills match workload requirements")
            
            skills_results = {
                "skill_gaps_identified": [],
                "skill_updates_required": [],
                "agents_retrained": [],
                "new_skills_acquired": [],
                "workforce_optimized": False,
                "analysis_time": datetime.now().isoformat()
            }
            
            # Analyze current skill requirements
            skill_requirements = await self._analyze_skill_requirements()
            
            # Assess current agent skills
            skill_assessment = await self._assess_agent_skills(skill_requirements)
            
            # Identify skill gaps
            skill_gaps = await self._identify_skill_gaps(skill_requirements, skill_assessment)
            skills_results["skill_gaps_identified"] = skill_gaps
            
            if not skill_gaps:
                logger.info("✅ All agent skills match current workload requirements")
                skills_results["workforce_optimized"] = True
                return skills_results
            
            # Plan skill updates
            skill_update_plan = await self._plan_skill_updates(skill_gaps)
            skills_results["skill_updates_required"] = skill_update_plan
            
            # Implement skill updates
            for update in skill_update_plan:
                agent_id = update["agent_id"]
                new_skills = update["new_skills"]
                
                # Update agent skills
                await self._update_agent_skills(agent_id, new_skills)
                skills_results["agents_retrained"].append(agent_id)
                skills_results["new_skills_acquired"].extend(new_skills)
            
            # Verify optimization
            optimized_assessment = await self._assess_agent_skills(skill_requirements)
            remaining_gaps = await self._identify_skill_gaps(skill_requirements, optimized_assessment)
            
            skills_results["workforce_optimized"] = len(remaining_gaps) == 0
            
            logger.info(f"✅ Agent skills optimization completed: {len(skills_results['agents_retrained'])} agents retrained")
            return skills_results
            
        except Exception as e:
            logger.error(f"❌ Agent skills optimization failed: {e}")
            return {}
    
    async def get_real_time_dashboard(self) -> Dict[str, Any]:
        """Get real-time operations dashboard"""
        try:
            logger.info("📊 Generating real-time operations dashboard")
            
            dashboard = {
                "timestamp": datetime.now().isoformat(),
                "system_overview": {},
                "agent_status": {},
                "workload_distribution": {},
                "performance_metrics": {},
                "alerts": [],
                "recommendations": []
            }
            
            # System overview
            dashboard["system_overview"] = {
                "total_agents": len(self.agent_metrics),
                "active_agents": len([m for m in self.agent_metrics.values() if m.status == AgentStatus.ACTIVE]),
                "idle_agents": len([m for m in self.agent_metrics.values() if m.status == AgentStatus.IDLE]),
                "system_utilization": sum(m.utilization_rate for m in self.agent_metrics.values()) / len(self.agent_metrics) if self.agent_metrics else 0,
                "average_performance": sum(m.performance_score for m in self.agent_metrics.values()) / len(self.agent_metrics) if self.agent_metrics else 0,
                "error_rate": sum(m.error_rate for m in self.agent_metrics.values()) / len(self.agent_metrics) if self.agent_metrics else 0
            }
            
            # Agent status breakdown
            agent_status_counts = {}
            for status in AgentStatus:
                count = len([m for m in self.agent_metrics.values() if m.status == status])
                agent_status_counts[status.value] = count
            dashboard["agent_status"] = agent_status_counts
            
            # Workload distribution
            dashboard["workload_distribution"] = await self._analyze_workload_distribution()
            
            # Performance metrics
            dashboard["performance_metrics"] = {
                "top_performers": [],
                "underperformers": [],
                "efficiency_trends": [],
                "bottlenecks": []
            }
            
            # Identify top and bottom performers
            sorted_agents = sorted(self.agent_metrics.items(), key=lambda x: x[1].performance_score, reverse=True)
            dashboard["performance_metrics"]["top_performers"] = [
                {"agent_id": agent_id, "score": metrics.performance_score, "type": metrics.agent_type.value}
                for agent_id, metrics in sorted_agents[:5]
            ]
            dashboard["performance_metrics"]["underperformers"] = [
                {"agent_id": agent_id, "score": metrics.performance_score, "type": metrics.agent_type.value}
                for agent_id, metrics in sorted_agents[-5:]
            ]
            
            # Generate alerts
            dashboard["alerts"] = await self._generate_alerts()
            
            # Generate recommendations
            dashboard["recommendations"] = await self._generate_dashboard_recommendations()
            
            logger.info("✅ Real-time operations dashboard generated")
            return dashboard
            
        except Exception as e:
            logger.error(f"❌ Dashboard generation failed: {e}")
            return {}
    
    async def generate_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        try:
            logger.info("📋 Generating optimization report")
            
            report = {
                "report_id": f"optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "generated_at": datetime.now().isoformat(),
                "period": "last_24_hours",
                "executive_summary": {},
                "agent_performance": {},
                "workload_analysis": {},
                "optimization_actions": {},
                "recommendations": {},
                "future_outlook": {}
            }
            
            # Executive summary
            monitoring_results = await self.monitor_all_agents()
            report["executive_summary"] = {
                "total_agents": monitoring_results["total_agents"],
                "system_health": monitoring_results["system_health"],
                "average_utilization": monitoring_results["average_utilization"],
                "average_performance": monitoring_results["average_performance"],
                "critical_issues": len([i for i in monitoring_results["issues"] if "critical" in i.lower()]),
                "optimization_opportunities": len(monitoring_results["recommendations"])
            }
            
            # Agent performance analysis
            report["agent_performance"] = {
                "performance_distribution": await self._analyze_performance_distribution(),
                "performance_trends": await self._analyze_performance_trends(),
                "skill_utilization": await self._analyze_skill_utilization(),
                "efficiency_metrics": await self._calculate_efficiency_metrics()
            }
            
            # Workload analysis
            report["workload_analysis"] = {
                "current_distribution": await self._analyze_workload_distribution(),
                "bottleneck_analysis": await self._analyze_bottlenecks(),
                "capacity_utilization": await self._analyze_capacity_utilization(),
                "workload_forecast": await self._forecast_workload()
            }
            
            # Optimization actions taken
            report["optimization_actions"] = {
                "idle_agent_elimination": await self.eliminate_idle_agents(),
                "skills_optimization": await self.ensure_agent_skills_match_workload(),
                "allocation_optimization": await self.optimize_agent_allocation(),
                "performance_improvements": await self._analyze_performance_improvements()
            }
            
            # Recommendations
            report["recommendations"] = await self._generate_strategic_recommendations()
            
            # Future outlook
            report["future_outlook"] = {
                "predicted_growth": await self._predict_growth(),
                "resource_requirements": await self._calculate_resource_requirements(),
                "optimization_potential": await self._calculate_optimization_potential(),
                "risk_assessment": await self._assess_optimization_risks()
            }
            
            logger.info(f"✅ Optimization report generated: {report['report_id']}")
            return report
            
        except Exception as e:
            logger.error(f"❌ Optimization report generation failed: {e}")
            return {}
    
    # Private methods
    
    async def _load_agent_metrics(self):
        """Load agent metrics from Supabase"""
        try:
            # Simulate loading agent metrics
            agent_types = list(AgentType)
            
            for i, agent_type in enumerate(agent_types):
                for j in range(3):  # 3 agents per type
                    agent_id = f"{agent_type.value}_{j+1}"
                    
                    # Simulate varied metrics
                    status = AgentStatus.ACTIVE if i % 3 != 0 else AgentStatus.IDLE
                    utilization = 0.8 if status == AgentStatus.ACTIVE else 0.05
                    performance = 0.75 + (i * 0.05) + (j * 0.02)
                    
                    metrics = AgentMetrics(
                        agent_id=agent_id,
                        agent_type=agent_type,
                        status=status,
                        current_task=f"task_{i}_{j}" if status == AgentStatus.ACTIVE else None,
                        tasks_completed=10 + i * 5,
                        tasks_failed=1 if i % 5 == 0 else 0,
                        average_task_time=120.0 + (i * 10),
                        utilization_rate=utilization,
                        performance_score=performance,
                        last_active=datetime.now() - timedelta(hours=i),
                        skills=[f"skill_{k}" for k in range(3 + i)],
                        capacity=5,
                        current_load=int(utilization * 5),
                        error_rate=0.02 if performance > 0.8 else 0.08,
                        response_time_ms=150.0 + (i * 20)
                    )
                    
                    self.agent_metrics[agent_id] = metrics
            
            logger.info(f"📊 Loaded {len(self.agent_metrics)} agent metrics")
        except Exception as e:
            logger.error(f"Failed to load agent metrics: {e}")
    
    async def _initialize_monitoring(self):
        """Initialize monitoring system"""
        try:
            # Start monitoring loop
            asyncio.create_task(self._monitoring_loop())
            logger.info("🔍 Agent monitoring initialized")
        except Exception as e:
            logger.error(f"Failed to initialize monitoring: {e}")
    
    async def _setup_optimization_engine(self):
        """Setup optimization engine"""
        try:
            # Initialize optimization components
            logger.info("⚡ Optimization engine setup")
        except Exception as e:
            logger.error(f"Failed to setup optimization engine: {e}")
    
    async def _monitoring_loop(self):
        """Continuous monitoring loop"""
        while self.monitoring_active:
            try:
                # Update agent metrics
                await self._update_agent_metrics()
                
                # Check for optimization opportunities
                if self.optimization_enabled:
                    await self._check_optimization_opportunities()
                
                # Wait for next monitoring cycle
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(300)  # Wait longer on error
    
    async def _update_agent_metrics(self):
        """Update agent metrics"""
        try:
            # Simulate metric updates
            for agent_id, metrics in self.agent_metrics.items():
                # Update last active time for active agents
                if metrics.status == AgentStatus.ACTIVE:
                    metrics.last_active = datetime.now()
                    metrics.utilization_rate = min(1.0, metrics.utilization_rate + 0.01)
                
                # Random performance fluctuations
                import random
                metrics.performance_score = max(0.3, min(1.0, metrics.performance_score + random.uniform(-0.02, 0.02)))
                
        except Exception as e:
            logger.error(f"Failed to update agent metrics: {e}")
    
    async def _check_optimization_opportunities(self):
        """Check for optimization opportunities"""
        try:
            # Check for idle agents
            idle_count = len([m for m in self.agent_metrics.values() if m.status == AgentStatus.IDLE])
            
            if idle_count > len(self.agent_metrics) * 0.2:  # More than 20% idle
                await self.eliminate_idle_agents()
            
        except Exception as e:
            logger.error(f"Failed to check optimization opportunities: {e}")
    
    async def _generate_monitoring_recommendations(self, monitoring_results: Dict[str, Any]) -> List[str]:
        """Generate monitoring recommendations"""
        try:
            recommendations = []
            
            if monitoring_results["idle_agents"] > 0:
                recommendations.append(f"Redistribute work to {monitoring_results['idle_agents']} idle agents")
            
            if monitoring_results["average_performance"] < self.performance_threshold:
                recommendations.append("Implement performance improvement measures")
            
            if monitoring_results["error_agents"] > 0:
                recommendations.append("Address agent errors and implement recovery procedures")
            
            if monitoring_results["system_health"] != "healthy":
                recommendations.append("Conduct comprehensive system health assessment")
            
            return recommendations
        except Exception as e:
            logger.error(f"Failed to generate monitoring recommendations: {e}")
            return []
    
    async def _analyze_workload_distribution(self) -> Dict[str, Any]:
        """Analyze current workload distribution"""
        try:
            distribution = {
                "total_capacity": sum(m.capacity for m in self.agent_metrics.values()),
                "total_load": sum(m.current_load for m in self.agent_metrics.values()),
                "utilization_rate": 0.0,
                "agent_loads": {},
                "bottlenecks": [],
                "underutilized": []
            }
            
            for agent_id, metrics in self.agent_metrics.items():
                distribution["agent_loads"][agent_id] = {
                    "load": metrics.current_load,
                    "capacity": metrics.capacity,
                    "utilization": metrics.utilization_rate,
                    "type": metrics.agent_type.value
                }
                
                # Identify bottlenecks (over 90% utilization)
                if metrics.utilization_rate > self.overload_threshold:
                    distribution["bottlenecks"].append(agent_id)
                
                # Identify underutilized agents (under 30% utilization)
                if metrics.utilization_rate < 0.3:
                    distribution["underutilized"].append(agent_id)
            
            # Calculate overall utilization
            if distribution["total_capacity"] > 0:
                distribution["utilization_rate"] = distribution["total_load"] / distribution["total_capacity"]
            
            return distribution
        except Exception as e:
            logger.error(f"Failed to analyze workload distribution: {e}")
            return {}
    
    async def _identify_optimization_opportunities(self, distribution: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify optimization opportunities"""
        try:
            opportunities = []
            
            # Bottleneck optimization
            if distribution["bottlenecks"]:
                opportunities.append({
                    "type": "bottleneck",
                    "description": f"Reduce load on {len(distribution['bottlenecks'])} overloaded agents",
                    "priority": "high",
                    "potential_improvement": "20-30%"
                })
            
            # Underutilization optimization
            if distribution["underutilized"]:
                opportunities.append({
                    "type": "underutilization",
                    "description": f"Increase utilization of {len(distribution['underutilized'])} idle agents",
                    "priority": "medium",
                    "potential_improvement": "15-25%"
                })
            
            # Capacity optimization
            if distribution["utilization_rate"] > 0.8:
                opportunities.append({
                    "type": "capacity",
                    "description": "Scale resources to handle high utilization",
                    "priority": "high",
                    "potential_improvement": "25-35%"
                })
            
            return opportunities
        except Exception as e:
            logger.error(f"Failed to identify optimization opportunities: {e}")
            return []
    
    async def _generate_optimization_plan(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate optimization plan"""
        try:
            plan = []
            
            for opportunity in opportunities:
                if opportunity["type"] == "bottleneck":
                    plan.append({
                        "action": "redistribute_workload",
                        "target": opportunity["description"],
                        "steps": ["Identify overloaded agents", "Redistribute tasks", "Monitor performance"]
                    })
                elif opportunity["type"] == "underutilization":
                    plan.append({
                        "action": "eliminate_idle_agents",
                        "target": opportunity["description"],
                        "steps": ["Find idle agents", "Assign suitable tasks", "Track utilization"]
                    })
                elif opportunity["type"] == "capacity":
                    plan.append({
                        "action": "scale_resources",
                        "target": opportunity["description"],
                        "steps": ["Assess capacity needs", "Scale up resources", "Optimize allocation"]
                    })
            
            return plan
        except Exception as e:
            logger.error(f"Failed to generate optimization plan: {e}")
            return []
    
    async def _implement_optimizations(self, plan: List[Dict[str, Any]]) -> List[str]:
        """Implement optimization plan"""
        try:
            implemented = []
            
            for action in plan:
                action_type = action["action"]
                
                if action_type == "redistribute_workload":
                    await self.optimize_agent_allocation()
                    implemented.append("Workload redistribution completed")
                elif action_type == "eliminate_idle_agents":
                    await self.eliminate_idle_agents()
                    implemented.append("Idle agent elimination completed")
                elif action_type == "scale_resources":
                    # Simulate resource scaling
                    implemented.append("Resource scaling completed")
            
            return implemented
        except Exception as e:
            logger.error(f"Failed to implement optimizations: {e}")
            return []
    
    async def _calculate_efficiency_gain(self, current: Dict[str, Any], plan: List[Dict[str, Any]]) -> float:
        """Calculate expected efficiency gain"""
        try:
            # Simulate efficiency calculation
            base_gain = 0.15  # 15% base improvement
            
            for action in plan:
                if action["action"] == "eliminate_idle_agents":
                    base_gain += 0.10  # Additional 10% for idle elimination
                elif action["action"] == "redistribute_workload":
                    base_gain += 0.08  # Additional 8% for redistribution
            
            return min(base_gain, 0.5)  # Cap at 50%
        except Exception as e:
            logger.error(f"Failed to calculate efficiency gain: {e}")
            return 0.0
    
    async def _generate_optimal_distribution(self, plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate optimal workload distribution"""
        try:
            # Simulate optimal distribution
            optimal = {
                "target_utilization": 0.75,  # Target 75% utilization
                "balanced_load": True,
                "no_bottlenecks": True,
                "max_efficiency": True
            }
            
            return optimal
        except Exception as e:
            logger.error(f"Failed to generate optimal distribution: {e}")
            return {}
    
    async def _find_available_work(self, idle_agents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find available work for idle agents"""
        try:
            # Simulate finding available work
            available_work = []
            
            for agent in idle_agents:
                agent_type = agent["agent_type"]
                
                # Create sample work based on agent type
                work = {
                    "task_id": f"task_{agent_type.value}_{len(available_work)}",
                    "task_type": agent_type.value,
                    "priority": "medium",
                    "estimated_duration": 30,  # minutes
                    "required_skills": agent["skills"][:2]  # Use first 2 skills
                }
                
                available_work.append(work)
            
            return available_work
        except Exception as e:
            logger.error(f"Failed to find available work: {e}")
            return []
    
    async def _find_suitable_work(self, agent_type: AgentType, skills: List[str], available_work: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find suitable work for agent"""
        try:
            # Find work matching agent type and skills
            for work in available_work:
                if work["task_type"] == agent_type.value:
                    # Check skills match
                    required_skills = set(work.get("required_skills", []))
                    agent_skills = set(skills)
                    
                    if required_skills.issubset(agent_skills):
                        return work
            
            return None
        except Exception as e:
            logger.error(f"Failed to find suitable work: {e}")
            return None
    
    async def _assign_work_to_agent(self, agent_id: str, work: Dict[str, Any]):
        """Assign work to agent"""
        try:
            # Update agent metrics
            if agent_id in self.agent_metrics:
                metrics = self.agent_metrics[agent_id]
                metrics.current_task = work["task_id"]
                metrics.current_load += 1
                metrics.utilization_rate = metrics.current_load / metrics.capacity
                metrics.status = AgentStatus.BUSY
                
                logger.info(f"Assigned task {work['task_id']} to agent {agent_id}")
        except Exception as e:
            logger.error(f"Failed to assign work to agent: {e}")
    
    async def _update_agent_status(self, agent_id: str, status: AgentStatus):
        """Update agent status"""
        try:
            if agent_id in self.agent_metrics:
                self.agent_metrics[agent_id].status = status
        except Exception as e:
            logger.error(f"Failed to update agent status: {e}")
    
    async def _analyze_skill_requirements(self) -> Dict[str, List[str]]:
        """Analyze current skill requirements"""
        try:
            # Simulate skill requirements analysis
            requirements = {
                "research": ["data_analysis", "critical_thinking", "research_methodology"],
                "development": ["programming", "testing", "debugging", "version_control"],
                "planning": ["strategic_thinking", "project_management", "communication"],
                "innovation": ["creativity", "trend_analysis", "problem_solving"],
                "legal": ["malaysian_law", "contract_review", "compliance", "legal_research"]
            }
            
            return requirements
        except Exception as e:
            logger.error(f"Failed to analyze skill requirements: {e}")
            return {}
    
    async def _assess_agent_skills(self, requirements: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Assess current agent skills"""
        try:
            assessment = {}
            
            for agent_id, metrics in self.agent_metrics.items():
                assessment[agent_id] = metrics.skills
            
            return assessment
        except Exception as e:
            logger.error(f"Failed to assess agent skills: {e}")
            return {}
    
    async def _identify_skill_gaps(self, requirements: Dict[str, List[str]], assessment: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Identify skill gaps"""
        try:
            gaps = []
            
            for agent_id, skills in assessment.items():
                if agent_id in self.agent_metrics:
                    agent_type = self.agent_metrics[agent_id].agent_type.value
                    required_skills = requirements.get(agent_type, [])
                    
                    missing_skills = set(required_skills) - set(skills)
                    
                    if missing_skills:
                        gaps.append({
                            "agent_id": agent_id,
                            "agent_type": agent_type,
                            "missing_skills": list(missing_skills),
                            "priority": "high" if len(missing_skills) > 2 else "medium"
                        })
            
            return gaps
        except Exception as e:
            logger.error(f"Failed to identify skill gaps: {e}")
            return []
    
    async def _plan_skill_updates(self, skill_gaps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Plan skill updates"""
        try:
            plan = []
            
            for gap in skill_gaps:
                plan.append({
                    "agent_id": gap["agent_id"],
                    "new_skills": gap["missing_skills"],
                    "priority": gap["priority"],
                    "estimated_time": timedelta(days=len(gap["missing_skills"]) * 2)
                })
            
            return plan
        except Exception as e:
            logger.error(f"Failed to plan skill updates: {e}")
            return []
    
    async def _update_agent_skills(self, agent_id: str, new_skills: List[str]):
        """Update agent skills"""
        try:
            if agent_id in self.agent_metrics:
                self.agent_metrics[agent_id].skills.extend(new_skills)
                # Remove duplicates
                self.agent_metrics[agent_id].skills = list(set(self.agent_metrics[agent_id].skills))
                
                logger.info(f"Updated skills for agent {agent_id}: {new_skills}")
        except Exception as e:
            logger.error(f"Failed to update agent skills: {e}")
    
    async def _generate_alerts(self) -> List[Dict[str, Any]]:
        """Generate system alerts"""
        try:
            alerts = []
            
            # Check for critical issues
            error_agents = [agent_id for agent_id, metrics in self.agent_metrics.items() if metrics.status == AgentStatus.ERROR]
            if error_agents:
                alerts.append({
                    "level": "critical",
                    "message": f"{len(error_agents)} agents in error state",
                    "agents": error_agents
                })
            
            # Check for high idle rate
            idle_agents = [agent_id for agent_id, metrics in self.agent_metrics.items() if metrics.status == AgentStatus.IDLE]
            if len(idle_agents) > len(self.agent_metrics) * 0.3:
                alerts.append({
                    "level": "warning",
                    "message": f"High idle rate: {len(idle_agents)} agents idle",
                    "agents": idle_agents
                })
            
            # Check for performance issues
            low_performance = [agent_id for agent_id, metrics in self.agent_metrics.items() if metrics.performance_score < self.performance_threshold]
            if low_performance:
                alerts.append({
                    "level": "warning",
                    "message": f"{len(low_performance)} agents with low performance",
                    "agents": low_performance
                })
            
            return alerts
        except Exception as e:
            logger.error(f"Failed to generate alerts: {e}")
            return []
    
    async def _generate_dashboard_recommendations(self) -> List[str]:
        """Generate dashboard recommendations"""
        try:
            recommendations = []
            
            # Analyze current state
            idle_count = len([m for m in self.agent_metrics.values() if m.status == AgentStatus.IDLE])
            avg_performance = sum(m.performance_score for m in self.agent_metrics.values()) / len(self.agent_metrics) if self.agent_metrics else 0
            
            if idle_count > 0:
                recommendations.append(f"Redistribute work to {idle_count} idle agents")
            
            if avg_performance < self.performance_threshold:
                recommendations.append("Implement performance improvement measures")
            
            recommendations.append("Schedule regular agent skill assessments")
            recommendations.append("Monitor system utilization trends")
            
            return recommendations
        except Exception as e:
            logger.error(f"Failed to generate dashboard recommendations: {e}")
            return []
    
    def get_operations_status(self) -> Dict[str, Any]:
        """Get operations manager status"""
        try:
            return {
                "total_agents": len(self.agent_metrics),
                "monitoring_active": self.monitoring_active,
                "optimization_enabled": self.optimization_enabled,
                "recommendations_count": len(self.optimization_recommendations),
                "last_optimization": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get operations status: {e}")
            return {}
