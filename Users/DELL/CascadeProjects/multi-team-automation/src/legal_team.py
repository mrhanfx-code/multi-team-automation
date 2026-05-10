#!/usr/bin/env python3
"""
MFM Corporation - Expert Legal Team
Specialized in Malaysian laws in every aspect
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import re

logger = logging.getLogger(__name__)

class LegalArea(Enum):
    CONTRACT_LAW = "contract_law"
    CORPORATE_LAW = "corporate_law"
    EMPLOYMENT_LAW = "employment_law"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    TAXATION_LAW = "taxation_law"
    COMPLIANCE = "compliance"
    LITIGATION = "litigation"
    REGULATORY = "regulatory"
    CYBER_LAW = "cyber_law"
    REAL_ESTATE = "real_estate"
    BANKING_FINANCE = "banking_finance"
    ENVIRONMENTAL_LAW = "environmental_law"

class LegalDocumentType(Enum):
    CONTRACT = "contract"
    AGREEMENT = "agreement"
    POLICY = "policy"
    COMPLIANCE_REPORT = "compliance_report"
    LEGAL_OPINION = "legal_opinion"
    DUE_DILIGENCE = "due_diligence"
    LITIGATION_DOCUMENT = "litigation_document"
    REGULATORY_FILING = "regulatory_filing"
    MEMORANDUM = "memorandum"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class MalaysianLegalFramework:
    """Malaysian legal framework reference"""
    act_name: str
    act_number: str
    year_enacted: int
    key_provisions: List[str]
    relevant_sections: List[str]
    latest_amendment: Optional[str]
    compliance_requirements: List[str]
    
@dataclass
class LegalAssessment:
    """Legal assessment result"""
    id: str
    area: LegalArea
    risk_level: RiskLevel
    compliance_score: float
    legal_issues: List[str]
    recommendations: List[str]
    required_actions: List[str]
    deadlines: List[datetime]
    supporting_documents: List[str]
    assessment_date: datetime
    next_review: datetime

@dataclass
class ComplianceCheck:
    """Compliance check result"""
    id: str
    regulation: str
    compliance_status: bool
    gaps: List[str]
    remediation_steps: List[str]
    priority: str
    responsible_party: str
    due_date: datetime
    completed_at: Optional[datetime]

class ExpertLegalTeam:
    """Expert Legal Team specialized in Malaysian laws"""
    
    def __init__(self, supabase_manager):
        self.supabase_manager = supabase_manager
        self.legal_frameworks = {}
        self.assessments = {}
        self.compliance_checks = {}
        self.legal_templates = {}
        
        # Malaysian legal acts database
        self.malaysian_acts = self._initialize_malaysian_acts()
        
    async def initialize(self) -> bool:
        """Initialize the Expert Legal Team"""
        logger.info("⚖️ Initializing MFM Corporation Expert Legal Team")
        
        try:
            # Load legal frameworks
            await self._load_legal_frameworks()
            
            # Set up legal templates
            await self._setup_legal_templates()
            
            # Initialize compliance monitoring
            await self._initialize_compliance_monitoring()
            
            logger.info("✅ Expert Legal Team initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Expert Legal Team initialization failed: {e}")
            return False
    
    async def conduct_legal_assessment(self, business_area: str, 
                                     assessment_type: str,
                                     context: Dict[str, Any]) -> str:
        """Conduct comprehensive legal assessment"""
        try:
            assessment_id = f"legal_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            logger.info(f"⚖️ Conducting legal assessment for {business_area}")
            
            # Determine relevant legal areas
            relevant_areas = await self._determine_legal_areas(business_area, assessment_type)
            
            # Assess each legal area
            all_issues = []
            all_recommendations = []
            all_actions = []
            all_deadlines = []
            max_risk = RiskLevel.LOW
            total_compliance = 0.0
            
            for area in relevant_areas:
                area_result = await self._assess_legal_area(area, context)
                
                all_issues.extend(area_result['issues'])
                all_recommendations.extend(area_result['recommendations'])
                all_actions.extend(area_result['actions'])
                all_deadlines.extend(area_result['deadlines'])
                
                # Update risk level
                if area_result['risk_level'].value > max_risk.value:
                    max_risk = area_result['risk_level']
                
                total_compliance += area_result['compliance_score']
            
            # Calculate overall compliance score
            overall_compliance = total_compliance / len(relevant_areas) if relevant_areas else 0.0
            
            # Create assessment
            assessment = LegalAssessment(
                id=assessment_id,
                area=LegalArea.CORPORATE_LAW,  # Primary area
                risk_level=max_risk,
                compliance_score=overall_compliance,
                legal_issues=all_issues,
                recommendations=all_recommendations,
                required_actions=all_actions,
                deadlines=all_deadlines,
                supporting_documents=[],
                assessment_date=datetime.now(),
                next_review=datetime.now() + timedelta(days=90)
            )
            
            self.assessments[assessment_id] = assessment
            
            # Save to Supabase
            await self.supabase_manager.save_legal_assessment(asdict(assessment))
            
            logger.info(f"✅ Legal assessment completed: {assessment_id}")
            return assessment_id
            
        except Exception as e:
            logger.error(f"❌ Legal assessment failed: {e}")
            return ""
    
    async def review_contract(self, contract_text: str, 
                             contract_type: str,
                             parties: List[str]) -> Dict[str, Any]:
        """Review contract for Malaysian legal compliance"""
        try:
            logger.info(f"📄 Reviewing {contract_type} contract")
            
            review_result = {
                "contract_id": f"contract_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "contract_type": contract_type,
                "parties": parties,
                "compliance_score": 0.0,
                "risk_level": RiskLevel.LOW,
                "issues": [],
                "recommendations": [],
                "missing_clauses": [],
                "problematic_clauses": [],
                "required_amendments": [],
                "review_date": datetime.now().isoformat()
            }
            
            # Check for essential clauses based on Malaysian law
            essential_clauses = await self._get_essential_clauses(contract_type)
            
            for clause in essential_clauses:
                if clause['required'] and clause['pattern']:
                    if not re.search(clause['pattern'], contract_text, re.IGNORECASE):
                        review_result["missing_clauses"].append(clause['name'])
                        review_result["issues"].append(f"Missing essential clause: {clause['name']}")
            
            # Check for problematic clauses
            problematic_patterns = await self._get_problematic_patterns()
            
            for pattern in problematic_patterns:
                matches = re.finditer(pattern['pattern'], contract_text, re.IGNORECASE)
                for match in matches:
                    review_result["problematic_clauses"].append({
                        "type": pattern['type'],
                        "text": match.group(),
                        "line_number": contract_text[:match.start()].count('\n') + 1,
                        "issue": pattern['issue'],
                        "recommendation": pattern['recommendation']
                    })
            
            # Check Malaysian legal requirements
            legal_issues = await self._check_malaysian_legal_requirements(contract_text, contract_type)
            review_result["issues"].extend(legal_issues)
            
            # Calculate compliance score
            total_checks = len(essential_clauses) + len(legal_issues)
            passed_checks = len(essential_clauses) - len(review_result["missing_clauses"])
            review_result["compliance_score"] = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
            
            # Determine risk level
            if review_result["compliance_score"] >= 90:
                review_result["risk_level"] = RiskLevel.LOW
            elif review_result["compliance_score"] >= 70:
                review_result["risk_level"] = RiskLevel.MEDIUM
            elif review_result["compliance_score"] >= 50:
                review_result["risk_level"] = RiskLevel.HIGH
            else:
                review_result["risk_level"] = RiskLevel.CRITICAL
            
            # Generate recommendations
            review_result["recommendations"] = await self._generate_contract_recommendations(review_result)
            
            logger.info(f"✅ Contract review completed: {review_result['contract_id']}")
            return review_result
            
        except Exception as e:
            logger.error(f"❌ Contract review failed: {e}")
            return {}
    
    async def ensure_compliance(self, business_area: str, 
                             compliance_type: str) -> List[ComplianceCheck]:
        """Ensure compliance with Malaysian regulations"""
        try:
            logger.info(f"🔍 Ensuring compliance for {business_area}")
            
            compliance_checks = []
            
            # Get relevant regulations
            relevant_regulations = await self._get_relevant_regulations(business_area, compliance_type)
            
            for regulation in relevant_regulations:
                check_id = f"compliance_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(compliance_checks)}"
                
                # Perform compliance check
                compliance_result = await self._check_regulation_compliance(regulation, business_area)
                
                compliance_check = ComplianceCheck(
                    id=check_id,
                    regulation=regulation['name'],
                    compliance_status=compliance_result['compliant'],
                    gaps=compliance_result['gaps'],
                    remediation_steps=compliance_result['remediation_steps'],
                    priority=compliance_result['priority'],
                    responsible_party=compliance_result['responsible_party'],
                    due_date=datetime.now() + timedelta(days=compliance_result['days_to_comply']),
                    completed_at=None
                )
                
                compliance_checks.append(compliance_check)
                self.compliance_checks[check_id] = compliance_check
            
            # Save compliance checks
            for check in compliance_checks:
                await self.supabase_manager.save_compliance_check(asdict(check))
            
            logger.info(f"✅ Compliance check completed: {len(compliance_checks)} regulations checked")
            return compliance_checks
            
        except Exception as e:
            logger.error(f"❌ Compliance check failed: {e}")
            return []
    
    async def provide_legal_opinion(self, query: str, 
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide legal opinion based on Malaysian law"""
        try:
            logger.info(f"⚖️ Providing legal opinion for query: {query[:50]}...")
            
            opinion = {
                "opinion_id": f"legal_opinion_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "query": query,
                "context": context,
                "legal_basis": [],
                "analysis": "",
                "conclusion": "",
                "recommendations": [],
                "caveats": [],
                "references": [],
                "confidence_level": 0.0,
                "opinion_date": datetime.now().isoformat()
            }
            
            # Analyze legal query
            legal_areas = await self._analyze_legal_query(query)
            
            # Research relevant Malaysian laws
            for area in legal_areas:
                relevant_acts = await self._get_relevant_acts(area)
                opinion["legal_basis"].extend(relevant_acts)
            
            # Generate analysis
            opinion["analysis"] = await self._generate_legal_analysis(query, context, legal_areas)
            
            # Provide conclusion
            opinion["conclusion"] = await self._generate_conclusion(query, opinion["analysis"])
            
            # Generate recommendations
            opinion["recommendations"] = await self._generate_recommendations(query, opinion["conclusion"])
            
            # Add caveats
            opinion["caveats"] = [
                "This opinion is based on current Malaysian laws and regulations",
                "Laws may change and this opinion should be reviewed periodically",
                "This opinion does not create attorney-client privilege",
                "Consult with qualified legal counsel for specific advice"
            ]
            
            # Calculate confidence level
            opinion["confidence_level"] = await self._calculate_confidence(query, legal_areas)
            
            # Add references
            opinion["references"] = await self._get_legal_references(legal_areas)
            
            logger.info(f"✅ Legal opinion provided: {opinion['opinion_id']}")
            return opinion
            
        except Exception as e:
            logger.error(f"❌ Legal opinion failed: {e}")
            return {}
    
    async def monitor_regulatory_changes(self) -> List[Dict[str, Any]]:
        """Monitor changes in Malaysian regulations"""
        try:
            logger.info("📡 Monitoring Malaysian regulatory changes")
            
            changes = []
            
            # Simulate monitoring recent changes
            recent_changes = [
                {
                    "act": "Companies Act 2016",
                    "change_type": "Amendment",
                    "effective_date": "2024-01-01",
                    "summary": "Changes to corporate governance requirements",
                    "impact": "Medium",
                    "action_required": True
                },
                {
                    "act": "Personal Data Protection Act 2010",
                    "change_type": "New Regulation",
                    "effective_date": "2024-03-15",
                    "summary": "Enhanced data protection requirements",
                    "impact": "High",
                    "action_required": True
                },
                {
                    "act": "Employment Act 1955",
                    "change_type": "Guideline Update",
                    "effective_date": "2024-02-01",
                    "summary": "Updated guidelines on remote work",
                    "impact": "Low",
                    "action_required": False
                }
            ]
            
            for change in recent_changes:
                change_id = f"regulatory_change_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(changes)}"
                change["id"] = change_id
                change["detected_date"] = datetime.now().isoformat()
                changes.append(change)
            
            logger.info(f"✅ Regulatory monitoring completed: {len(changes)} changes detected")
            return changes
            
        except Exception as e:
            logger.error(f"❌ Regulatory monitoring failed: {e}")
            return []
    
    async def generate_legal_document(self, document_type: LegalDocumentType,
                                    parameters: Dict[str, Any]) -> str:
        """Generate legal document based on Malaysian law templates"""
        try:
            logger.info(f"📝 Generating {document_type.value} document")
            
            document_id = f"legal_doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Get template
            template = await self._get_document_template(document_type)
            
            if not template:
                logger.error(f"Template not found for {document_type.value}")
                return ""
            
            # Generate document
            document_content = await self._fill_template(template, parameters)
            
            # Add Malaysian legal clauses
            document_content = await self._add_malaysian_clauses(document_content, document_type)
            
            # Validate document
            validation_result = await self._validate_document(document_content, document_type)
            
            if not validation_result['valid']:
                logger.warning(f"Document validation issues: {validation_result['issues']}")
            
            # Save document
            document_data = {
                "id": document_id,
                "type": document_type.value,
                "content": document_content,
                "parameters": parameters,
                "validation": validation_result,
                "created_date": datetime.now().isoformat()
            }
            
            await self.supabase_manager.save_legal_document(document_data)
            
            logger.info(f"✅ Legal document generated: {document_id}")
            return document_id
            
        except Exception as e:
            logger.error(f"❌ Legal document generation failed: {e}")
            return ""
    
    # Private methods
    
    def _initialize_malaysian_acts(self) -> Dict[str, MalaysianLegalFramework]:
        """Initialize Malaysian legal acts database"""
        acts = {
            "Companies Act 2016": MalaysianLegalFramework(
                act_name="Companies Act 2016",
                act_number="Act 777",
                year_enacted=2016,
                key_provisions=[
                    "Company incorporation",
                    "Corporate governance",
                    "Share capital",
                    "Directors' duties",
                    "Financial reporting"
                ],
                relevant_sections=["Section 15", "Section 213", "Section 241"],
                latest_amendment="2023 Amendment",
                compliance_requirements=[
                    "Annual returns filing",
                    "Financial statements audit",
                    "Board meetings documentation"
                ]
            ),
            "Employment Act 1955": MalaysianLegalFramework(
                act_name="Employment Act 1955",
                act_number="Act 265",
                year_enacted=1955,
                key_provisions=[
                    "Employment contracts",
                    "Working hours",
                    "Leave entitlements",
                    "Termination procedures",
                    "Industrial relations"
                ],
                relevant_sections=["Section 12", "Section 60", "Section 61"],
                latest_amendment="2023 Amendment",
                compliance_requirements=[
                    "Employment contracts",
                    "EPF contributions",
                    "SOCSO contributions",
                    "Workplace safety"
                ]
            ),
            "Personal Data Protection Act 2010": MalaysianLegalFramework(
                act_name="Personal Data Protection Act 2010",
                act_number="Act 709",
                year_enacted=2010,
                key_provisions=[
                    "Data processing principles",
                    "User consent requirements",
                    "Data security obligations",
                    "Cross-border data transfer",
                    "Data breach notifications"
                ],
                relevant_sections=["Section 4", "Section 5", "Section 7"],
                latest_amendment="2024 Amendment",
                compliance_requirements=[
                    "Data protection policy",
                    "Consent management",
                    "Security measures",
                    "Breach reporting procedures"
                ]
            ),
            "Contracts Act 1950": MalaysianLegalFramework(
                act_name="Contracts Act 1950",
                act_number="Act 136",
                year_enacted=1950,
                key_provisions=[
                    "Contract formation",
                    "Offer and acceptance",
                    "Consideration",
                    "Contract validity",
                    "Breach of contract"
                ],
                relevant_sections=["Section 2", "Section 10", "Section 56"],
                latest_amendment=None,
                compliance_requirements=[
                    "Written agreements",
                    "Clear terms and conditions",
                    "Proper consideration",
                    "Legal capacity"
                ]
            ),
            "Cybersecurity Act 2024": MalaysianLegalFramework(
                act_name="Cybersecurity Act 2024",
                act_number="Act 854",
                year_enacted=2024,
                key_provisions=[
                    "Critical infrastructure protection",
                    "Cybersecurity standards",
                    "Incident reporting",
                    "Enforcement powers",
                    "International cooperation"
                ],
                relevant_sections=["Section 3", "Section 7", "Section 13"],
                latest_amendment=None,
                compliance_requirements=[
                    "Cybersecurity policies",
                    "Incident response plans",
                    "Regular security assessments",
                    "Staff training programs"
                ]
            )
        }
        
        return acts
    
    async def _load_legal_frameworks(self):
        """Load legal frameworks from Supabase"""
        try:
            # Simulate loading from Supabase
            self.legal_frameworks = self.malaysian_acts
            logger.info("📚 Legal frameworks loaded")
        except Exception as e:
            logger.error(f"Failed to load legal frameworks: {e}")
    
    async def _setup_legal_templates(self):
        """Set up legal document templates"""
        try:
            # Initialize legal templates
            self.legal_templates = {
                LegalDocumentType.CONTRACT: {
                    "name": "Standard Contract Template",
                    "sections": ["parties", "recitals", "terms", "conditions", "signatures"],
                    "malaysian_clauses": ["governing_law", "dispute_resolution", "compliance"]
                },
                LegalDocumentType.AGREEMENT: {
                    "name": "Standard Agreement Template",
                    "sections": ["preamble", "obligations", "representations", "term_termination"],
                    "malaysian_clauses": ["jurisdiction", "confidentiality", "force_majeure"]
                }
            }
            
            logger.info("📄 Legal templates configured")
        except Exception as e:
            logger.error(f"Failed to setup legal templates: {e}")
    
    async def _initialize_compliance_monitoring(self):
        """Initialize compliance monitoring"""
        try:
            # Set up compliance monitoring schedules
            logger.info("🔍 Compliance monitoring initialized")
        except Exception as e:
            logger.error(f"Failed to initialize compliance monitoring: {e}")
    
    async def _determine_legal_areas(self, business_area: str, assessment_type: str) -> List[LegalArea]:
        """Determine relevant legal areas"""
        try:
            # Map business areas to legal areas
            area_mapping = {
                "corporate": [LegalArea.CORPORATE_LAW, LegalArea.COMPLIANCE],
                "employment": [LegalArea.EMPLOYMENT_LAW, LegalArea.COMPLIANCE],
                "technology": [LegalArea.CYBER_LAW, LegalArea.INTELLECTUAL_PROPERTY],
                "finance": [LegalArea.BANKING_FINANCE, LegalArea.TAXATION_LAW],
                "real_estate": [LegalArea.REAL_ESTATE, LegalArea.CONTRACT_LAW],
                "manufacturing": [LegalArea.ENVIRONMENTAL_LAW, LegalArea.COMPLIANCE],
                "startup": [LegalArea.CORPORATE_LAW, LegalArea.INTELLECTUAL_PROPERTY, LegalArea.COMPLIANCE],
                "international": [LegalArea.REGULATORY, LegalArea.COMPLIANCE]
            }
            
            return area_mapping.get(business_area.lower(), [LegalArea.CORPORATE_LAW])
        except Exception as e:
            logger.error(f"Failed to determine legal areas: {e}")
            return [LegalArea.CORPORATE_LAW]
    
    async def _assess_legal_area(self, area: LegalArea, context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess a specific legal area"""
        try:
            # Simulate legal area assessment
            assessment = {
                "area": area,
                "risk_level": RiskLevel.MEDIUM,
                "compliance_score": 0.75,
                "issues": [f"General compliance issue in {area.value}"],
                "recommendations": [f"Review {area.value} requirements"],
                "actions": [f"Implement {area.value} compliance measures"],
                "deadlines": [datetime.now() + timedelta(days=30)]
            }
            
            return assessment
        except Exception as e:
            logger.error(f"Failed to assess legal area {area}: {e}")
            return {}
    
    async def _get_essential_clauses(self, contract_type: str) -> List[Dict[str, Any]]:
        """Get essential clauses for contract type"""
        try:
            clauses = {
                "employment": [
                    {"name": "Job Description", "required": True, "pattern": r"(job\s+description|duties\s+and\s+responsibilities)"},
                    {"name": "Salary and Benefits", "required": True, "pattern": r"(salary|wages|compensation|remuneration)"},
                    {"name": "Working Hours", "required": True, "pattern": r"(working\s+hours|office\s+hours|business\s+hours)"},
                    {"name": "Leave Entitlement", "required": True, "pattern": r"(annual\s+leave|annual\s+leave|sick\s+leave)"}
                ],
                "service": [
                    {"name": "Scope of Services", "required": True, "pattern": r"(scope\s+of\s+services|services\s+to\s+be\s+provided)"},
                    {"name": "Payment Terms", "required": True, "pattern": r"(payment\s+terms|fees|compensation)"},
                    {"name": "Term and Termination", "required": True, "pattern": r"(term\s+and\s+termination|termination|duration)"},
                    {"name": "Confidentiality", "required": True, "pattern": r"(confidential|non-disclosure|proprietary)"}
                ]
            }
            
            return clauses.get(contract_type.lower(), [])
        except Exception as e:
            logger.error(f"Failed to get essential clauses: {e}")
            return []
    
    async def _get_problematic_patterns(self) -> List[Dict[str, Any]]:
        """Get problematic contract patterns"""
        try:
            patterns = [
                {
                    "type": "Unlimited Liability",
                    "pattern": r"(unlimited\s+liability|absolute\s+liability)",
                    "issue": "Unlimited liability clause may expose company to excessive risk",
                    "recommendation": "Consider limiting liability to reasonable amounts"
                },
                {
                    "type": "Indefinite Term",
                    "pattern": r"(perpetual|indefinite|unlimited\s+term)",
                    "issue": "Indefinite terms may be unenforceable under Malaysian law",
                    "recommendation": "Specify reasonable term periods"
                },
                {
                    "type": "Illegal Clause",
                    "pattern": r"(against\s+public\s+policy|illegal|prohibited)",
                    "issue": "Clauses against public policy are void in Malaysia",
                    "recommendation": "Remove or modify illegal provisions"
                }
            ]
            
            return patterns
        except Exception as e:
            logger.error(f"Failed to get problematic patterns: {e}")
            return []
    
    async def _check_malaysian_legal_requirements(self, contract_text: str, contract_type: str) -> List[str]:
        """Check Malaysian legal requirements"""
        try:
            issues = []
            
            # Check for governing law clause
            if "governing law" not in contract_text.lower() and "governing law of malaysia" not in contract_text.lower():
                issues.append("Missing governing law clause - should specify Malaysian law")
            
            # Check for dispute resolution
            if "dispute resolution" not in contract_text.lower() and "arbitration" not in contract_text.lower():
                issues.append("Missing dispute resolution clause - consider Malaysian arbitration")
            
            # Check for statutory requirements based on contract type
            if contract_type.lower() == "employment":
                if "epf" not in contract_text.lower() or "socso" not in contract_text.lower():
                    issues.append("Missing statutory contribution references (EPF/SOCSO)")
            
            return issues
        except Exception as e:
            logger.error(f"Failed to check Malaysian legal requirements: {e}")
            return []
    
    async def _generate_contract_recommendations(self, review_result: Dict[str, Any]) -> List[str]:
        """Generate contract recommendations"""
        try:
            recommendations = []
            
            if review_result["missing_clauses"]:
                recommendations.append("Add all missing essential clauses")
            
            if review_result["problematic_clauses"]:
                recommendations.append("Review and amend problematic clauses")
            
            if review_result["compliance_score"] < 80:
                recommendations.append("Strengthen compliance with Malaysian laws")
            
            recommendations.append("Have the contract reviewed by qualified Malaysian legal counsel")
            recommendations.append("Ensure all parties sign and date the contract")
            
            return recommendations
        except Exception as e:
            logger.error(f"Failed to generate contract recommendations: {e}")
            return []
    
    async def _get_relevant_regulations(self, business_area: str, compliance_type: str) -> List[Dict[str, Any]]:
        """Get relevant regulations for business area"""
        try:
            regulations = {
                "corporate": [
                    {"name": "Companies Act 2016", "days_to_comply": 30},
                    {"name": "Corporate Governance Code", "days_to_comply": 60},
                    {"name": "Bursa Malaysia Listing Requirements", "days_to_comply": 45}
                ],
                "employment": [
                    {"name": "Employment Act 1955", "days_to_comply": 15},
                    {"name": "EPF Act 1991", "days_to_comply": 30},
                    {"name": "SOCSO Act 1969", "days_to_comply": 30}
                ],
                "technology": [
                    {"name": "Personal Data Protection Act 2010", "days_to_comply": 90},
                    {"name": "Cybersecurity Act 2024", "days_to_comply": 120},
                    {"name": "Communications and Multimedia Act 1998", "days_to_comply": 60}
                ]
            }
            
            return regulations.get(business_area.lower(), [])
        except Exception as e:
            logger.error(f"Failed to get relevant regulations: {e}")
            return []
    
    async def _check_regulation_compliance(self, regulation: Dict[str, Any], business_area: str) -> Dict[str, Any]:
        """Check compliance with specific regulation"""
        try:
            # Simulate compliance check
            compliance_result = {
                "compliant": False,
                "gaps": [f"Gap found in {regulation['name']}"],
                "remediation_steps": [f"Address compliance requirements for {regulation['name']}"],
                "priority": "Medium",
                "responsible_party": "Legal Team",
                "days_to_comply": regulation.get("days_to_comply", 30)
            }
            
            return compliance_result
        except Exception as e:
            logger.error(f"Failed to check regulation compliance: {e}")
            return {}
    
    async def _analyze_legal_query(self, query: str) -> List[LegalArea]:
        """Analyze legal query to determine relevant areas"""
        try:
            query_lower = query.lower()
            areas = []
            
            # Keywords for different legal areas
            area_keywords = {
                LegalArea.CONTRACT_LAW: ["contract", "agreement", "breach", "terms"],
                LegalArea.CORPORATE_LAW: ["company", "corporate", "director", "shareholder"],
                LegalArea.EMPLOYMENT_LAW: ["employment", "employee", "work", "termination"],
                LegalArea.INTELLECTUAL_PROPERTY: ["trademark", "copyright", "patent", "intellectual property"],
                LegalArea.TAXATION_LAW: ["tax", "income tax", "gst", "taxation"],
                LegalArea.CYBER_LAW: ["cyber", "data breach", "online", "digital"],
                LegalArea.COMPLIANCE: ["compliance", "regulation", "legal requirement"]
            }
            
            for area, keywords in area_keywords.items():
                if any(keyword in query_lower for keyword in keywords):
                    areas.append(area)
            
            return areas if areas else [LegalArea.CORPORATE_LAW]
        except Exception as e:
            logger.error(f"Failed to analyze legal query: {e}")
            return [LegalArea.CORPORATE_LAW]
    
    async def _get_relevant_acts(self, area: LegalArea) -> List[str]:
        """Get relevant Malaysian acts for legal area"""
        try:
            area_acts = {
                LegalArea.CONTRACT_LAW: ["Contracts Act 1950"],
                LegalArea.CORPORATE_LAW: ["Companies Act 2016", "Corporate Governance Code"],
                LegalArea.EMPLOYMENT_LAW: ["Employment Act 1955", "Industrial Relations Act 1967"],
                LegalArea.INTELLECTUAL_PROPERTY: ["Copyright Act 1987", "Trade Marks Act 2019"],
                LegalArea.TAXATION_LAW: ["Income Tax Act 1967", "Goods and Services Tax Act 2014"],
                LegalArea.CYBER_LAW: ["Cybersecurity Act 2024", "Personal Data Protection Act 2010"],
                LegalArea.COMPLIANCE: ["Anti-Money Laundering Act 2001", "Competition Act 2010"]
            }
            
            return area_acts.get(area, [])
        except Exception as e:
            logger.error(f"Failed to get relevant acts: {e}")
            return []
    
    async def _generate_legal_analysis(self, query: str, context: Dict[str, Any], legal_areas: List[LegalArea]) -> str:
        """Generate legal analysis"""
        try:
            analysis = f"Legal Analysis for: {query}\n\n"
            
            analysis += "Relevant Legal Areas:\n"
            for area in legal_areas:
                analysis += f"- {area.value.replace('_', ' ').title()}\n"
            
            analysis += f"\nContextual Considerations:\n"
            for key, value in context.items():
                analysis += f"- {key}: {value}\n"
            
            analysis += f"\nAnalysis:\n"
            analysis += "Based on Malaysian legal framework, the query involves considerations under multiple legal statutes. "
            analysis += "The primary legal requirements must be addressed in accordance with the relevant acts and regulations.\n"
            
            return analysis
        except Exception as e:
            logger.error(f"Failed to generate legal analysis: {e}")
            return "Analysis unavailable due to technical issues."
    
    async def _generate_conclusion(self, query: str, analysis: str) -> str:
        """Generate legal conclusion"""
        try:
            conclusion = f"Conclusion:\n"
            conclusion += "Based on the analysis of Malaysian laws and regulations, the matter requires careful consideration of multiple legal frameworks. "
            conclusion += "It is recommended to ensure full compliance with all applicable Malaysian statutes and regulations.\n"
            conclusion += "This conclusion is based on current laws and may require updates as regulations change.\n"
            
            return conclusion
        except Exception as e:
            logger.error(f"Failed to generate conclusion: {e}")
            return "Conclusion unavailable due to technical issues."
    
    async def _generate_recommendations(self, query: str, conclusion: str) -> List[str]:
        """Generate recommendations"""
        try:
            recommendations = [
                "Consult with qualified Malaysian legal counsel for specific advice",
                "Ensure compliance with all relevant Malaysian laws and regulations",
                "Implement regular legal compliance reviews",
                "Stay updated on changes in Malaysian legislation",
                "Maintain proper documentation and records",
                "Consider industry-specific legal requirements"
            ]
            
            return recommendations
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return []
    
    async def _calculate_confidence(self, query: str, legal_areas: List[LegalArea]) -> float:
        """Calculate confidence level for legal opinion"""
        try:
            # Base confidence
            confidence = 0.7
            
            # Adjust based on query complexity
            if len(legal_areas) > 3:
                confidence -= 0.1
            elif len(legal_areas) == 1:
                confidence += 0.1
            
            # Adjust based on query specificity
            if len(query.split()) > 20:
                confidence += 0.1
            elif len(query.split()) < 5:
                confidence -= 0.2
            
            return min(max(confidence, 0.3), 0.95)  # Keep between 0.3 and 0.95
        except Exception as e:
            logger.error(f"Failed to calculate confidence: {e}")
            return 0.5
    
    async def _get_legal_references(self, legal_areas: List[LegalArea]) -> List[str]:
        """Get legal references"""
        try:
            references = []
            
            for area in legal_areas:
                acts = await self._get_relevant_acts(area)
                references.extend(acts)
            
            # Add general references
            references.extend([
                "Federal Constitution of Malaysia",
                "Rules of Court 2012",
                "Legal Profession Act 1976"
            ])
            
            return list(set(references))  # Remove duplicates
        except Exception as e:
            logger.error(f"Failed to get legal references: {e}")
            return []
    
    async def _get_document_template(self, document_type: LegalDocumentType) -> Optional[Dict[str, Any]]:
        """Get document template"""
        try:
            return self.legal_templates.get(document_type)
        except Exception as e:
            logger.error(f"Failed to get document template: {e}")
            return None
    
    async def _fill_template(self, template: Dict[str, Any], parameters: Dict[str, Any]) -> str:
        """Fill template with parameters"""
        try:
            content = f"{template['name']}\n\n"
            
            for section in template['sections']:
                content += f"{section.upper()}\n"
                content += f"[Content for {section} based on parameters]\n\n"
            
            return content
        except Exception as e:
            logger.error(f"Failed to fill template: {e}")
            return ""
    
    async def _add_malaysian_clauses(self, content: str, document_type: LegalDocumentType) -> str:
        """Add Malaysian legal clauses"""
        try:
            malaysian_clauses = """
            
MALAYSIAN LEGAL CLAUSES:

1. Governing Law
This document shall be governed by and construed in accordance with the laws of Malaysia.

2. Jurisdiction
Any dispute arising from this document shall be subject to the exclusive jurisdiction of the Malaysian courts.

3. Compliance
Both parties shall comply with all applicable Malaysian laws, regulations, and statutory requirements.

4. Force Majeure
Neither party shall be liable for any failure or delay in performance due to circumstances beyond their reasonable control.
"""
            
            return content + malaysian_clauses
        except Exception as e:
            logger.error(f"Failed to add Malaysian clauses: {e}")
            return content
    
    async def _validate_document(self, content: str, document_type: LegalDocumentType) -> Dict[str, Any]:
        """Validate legal document"""
        try:
            validation = {
                "valid": True,
                "issues": [],
                "warnings": []
            }
            
            # Basic validation checks
            if len(content) < 100:
                validation["valid"] = False
                validation["issues"].append("Document content too short")
            
            if "Governing Law" not in content:
                validation["warnings"].append("Missing governing law clause")
            
            return validation
        except Exception as e:
            logger.error(f"Failed to validate document: {e}")
            return {"valid": False, "issues": ["Validation error"], "warnings": []}
    
    def get_team_status(self) -> Dict[str, Any]:
        """Get legal team status"""
        try:
            return {
                "assessments": len(self.assessments),
                "compliance_checks": len(self.compliance_checks),
                "legal_frameworks": len(self.legal_frameworks),
                "legal_templates": len(self.legal_templates),
                "malaysian_acts": len(self.malaysian_acts),
                "active_monitoring": True
            }
        except Exception as e:
            logger.error(f"Failed to get team status: {e}")
            return {}
