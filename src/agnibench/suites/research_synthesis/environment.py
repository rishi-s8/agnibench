"""
Simulated environment for the research synthesis benchmark suite.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List

from agnibench.core.environment import SimulatedEnvironment
from agnibench.suites.research_synthesis.tools import (get_research_data,
                                                       set_research_data)


class ResearchEnvironment(SimulatedEnvironment):
    """
    Environment for research synthesis tasks.

    Manages documents, notes, and research state.
    """

    def _setup_default_state(self) -> None:
        """Set up default state with sample research documents."""
        # Sample documents for research tasks
        documents = [
            {
                "id": "doc_q4_report",
                "title": "Q4 Financial Performance Report",
                "type": "report",
                "author": "Finance Team",
                "created_at": (datetime.now() - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now() - timedelta(days=5)).isoformat(),
                "tags": ["finance", "quarterly", "performance"],
                "content": """Q4 Financial Performance Report

Executive Summary:
This quarter showed strong performance with revenue growth of 15% year-over-year. Key drivers include expansion in the enterprise segment and successful product launches.

Key Metrics:
- Total Revenue: $45.2M (up 15% YoY)
- Operating Margin: 22% (up 3 percentage points)
- Customer Acquisition Cost: $150 (down 10%)
- Customer Lifetime Value: $2,400 (up 8%)

Segment Performance:
- Enterprise: $28M (62% of revenue, up 20%)
- SMB: $12M (27% of revenue, up 8%)
- Consumer: $5.2M (11% of revenue, flat)

Challenges:
- Supply chain costs increased 5%
- Competition intensified in SMB segment
- Currency headwinds impacted international revenue

Outlook:
Q1 is expected to show continued momentum with 12-15% projected growth.""",
                "extracted_facts": [
                    "Revenue grew 15% year-over-year to $45.2M",
                    "Operating margin improved to 22%",
                    "Enterprise segment is 62% of revenue",
                    "Customer acquisition cost decreased 10%",
                    "Supply chain costs increased 5%",
                ],
                "comparisons": {
                    "doc_market_analysis": {
                        "similarities": [
                            "Both report strong enterprise growth",
                            "Both mention competitive pressures",
                        ],
                        "differences": [
                            "Financial report focuses on metrics, market analysis on trends"
                        ],
                        "contradictions": [],
                    }
                },
            },
            {
                "id": "doc_market_analysis",
                "title": "Market Analysis: Industry Trends 2024",
                "type": "analysis",
                "author": "Strategy Team",
                "created_at": (datetime.now() - timedelta(days=45)).isoformat(),
                "updated_at": (datetime.now() - timedelta(days=10)).isoformat(),
                "tags": ["market", "trends", "strategy"],
                "content": """Market Analysis: Industry Trends 2024

Market Overview:
The enterprise software market continues rapid expansion, with total addressable market reaching $600B globally. AI integration is the primary driver of growth.

Key Trends:
1. AI/ML Integration: 78% of enterprises plan to increase AI spending
2. Cloud Migration: Hybrid cloud adoption up 45%
3. Security Focus: Cybersecurity budgets increased 30%
4. Automation: Process automation ROI averaging 250%

Competitive Landscape:
- Market leader: TechCorp (25% share)
- We rank #3 with 12% market share
- Main competitors investing heavily in AI features
- Price competition increasing in SMB segment

Customer Insights:
- Enterprise buyers prioritize integration capabilities
- SMB buyers most price-sensitive
- Security certifications increasingly required

Recommendations:
1. Accelerate AI roadmap
2. Develop strategic partnerships
3. Focus on enterprise vertical expansion""",
                "extracted_facts": [
                    "Enterprise software TAM is $600B globally",
                    "78% of enterprises plan to increase AI spending",
                    "Company has 12% market share, ranking #3",
                    "Hybrid cloud adoption up 45%",
                    "Process automation shows 250% average ROI",
                ],
                "comparisons": {
                    "doc_q4_report": {
                        "similarities": [
                            "Both report strong enterprise growth",
                            "Both mention competitive pressures",
                        ],
                        "differences": [
                            "Financial report focuses on metrics, market analysis on trends"
                        ],
                        "contradictions": [],
                    },
                    "doc_product_roadmap": {
                        "similarities": ["Both emphasize AI importance"],
                        "differences": [
                            "Market analysis is external-focused, roadmap is internal"
                        ],
                        "contradictions": [],
                    },
                },
            },
            {
                "id": "doc_product_roadmap",
                "title": "Product Roadmap 2024",
                "type": "documentation",
                "author": "Product Team",
                "created_at": (datetime.now() - timedelta(days=60)).isoformat(),
                "updated_at": (datetime.now() - timedelta(days=3)).isoformat(),
                "tags": ["product", "roadmap", "planning"],
                "content": """Product Roadmap 2024

Vision:
Become the leading platform for AI-powered enterprise automation.

Q1 Priorities:
- Launch AI Assistant feature (Beta)
- Improve dashboard performance by 40%
- Release mobile app v2.0

Q2 Priorities:
- AI Assistant general availability
- Enterprise SSO enhancements
- API v3.0 with GraphQL support

Q3 Priorities:
- Advanced analytics dashboard
- Multi-language support (5 languages)
- Workflow automation builder

Q4 Priorities:
- AI-powered insights engine
- Enterprise security audit trail
- Platform performance optimization

Resource Allocation:
- Engineering: 60% new features, 30% maintenance, 10% technical debt
- Design: Focus on mobile experience and AI interfaces
- QA: Automated testing coverage target 85%

Dependencies:
- AI features require cloud infrastructure upgrade
- Mobile app depends on API v3.0
- Analytics requires data pipeline improvements

Risks:
- AI talent scarcity may delay timelines
- Third-party integrations complexity
- Regulatory compliance requirements""",
                "extracted_facts": [
                    "Vision is to lead AI-powered enterprise automation",
                    "AI Assistant launching in Q1 Beta, Q2 GA",
                    "Engineering allocation: 60% new features",
                    "Automated testing coverage target is 85%",
                    "AI talent scarcity identified as risk",
                ],
                "comparisons": {
                    "doc_market_analysis": {
                        "similarities": ["Both emphasize AI importance"],
                        "differences": [
                            "Market analysis is external-focused, roadmap is internal"
                        ],
                        "contradictions": [],
                    }
                },
            },
            {
                "id": "doc_customer_survey",
                "title": "Customer Satisfaction Survey Results",
                "type": "report",
                "author": "Customer Success Team",
                "created_at": (datetime.now() - timedelta(days=20)).isoformat(),
                "updated_at": (datetime.now() - timedelta(days=20)).isoformat(),
                "tags": ["customer", "survey", "satisfaction"],
                "content": """Customer Satisfaction Survey Results

Survey Overview:
- Respondents: 1,247 customers
- Response rate: 34%
- Survey period: Last 30 days

Overall Satisfaction:
- NPS Score: 42 (up from 38)
- Overall Satisfaction: 4.2/5
- Would Recommend: 87%

Top Strengths:
1. Product reliability (4.5/5)
2. Customer support quality (4.4/5)
3. Feature completeness (4.1/5)

Areas for Improvement:
1. Mobile experience (3.2/5)
2. Documentation quality (3.5/5)
3. Onboarding process (3.6/5)

Feature Requests:
1. Better reporting/analytics (45% requested)
2. More integrations (38% requested)
3. Improved mobile app (35% requested)
4. AI/automation features (32% requested)

Verbatim Highlights:
- "Great product but mobile app needs work"
- "Support team is excellent"
- "Would love more analytics capabilities"
- "Onboarding was confusing initially"

Comparison to Previous Quarter:
- NPS improved 4 points
- Mobile satisfaction declined
- Support satisfaction improved""",
                "extracted_facts": [
                    "NPS Score is 42, up from 38",
                    "Overall satisfaction is 4.2/5",
                    "Mobile experience rated only 3.2/5",
                    "45% of customers requested better analytics",
                    "87% would recommend the product",
                ],
                "comparisons": {
                    "doc_product_roadmap": {
                        "similarities": [
                            "Both identify mobile and analytics as priorities"
                        ],
                        "differences": [
                            "Survey is customer perspective, roadmap is company perspective"
                        ],
                        "contradictions": [],
                    }
                },
            },
            {
                "id": "doc_security_policy",
                "title": "Security Policy and Compliance",
                "type": "policy",
                "author": "Security Team",
                "created_at": (datetime.now() - timedelta(days=90)).isoformat(),
                "updated_at": (datetime.now() - timedelta(days=15)).isoformat(),
                "tags": ["security", "compliance", "policy"],
                "content": """Security Policy and Compliance

Certifications:
- SOC 2 Type II (Renewed annually)
- ISO 27001 (Valid through 2025)
- GDPR Compliant
- HIPAA Compliant (Healthcare customers)

Data Protection:
- All data encrypted at rest (AES-256)
- All data encrypted in transit (TLS 1.3)
- Customer data isolated by tenant
- Backups retained for 30 days

Access Control:
- Role-based access control (RBAC)
- Multi-factor authentication required
- Session timeout: 30 minutes
- Password requirements: 12+ characters, complexity rules

Incident Response:
- 24/7 security monitoring
- Incident response SLA: 1 hour
- Customer notification: Within 24 hours
- Post-incident review required

Compliance Requirements:
- Annual security audits
- Quarterly penetration testing
- Monthly vulnerability scans
- Continuous compliance monitoring

Recent Updates:
- Added support for SAML 2.0
- Enhanced audit logging
- Implemented zero-trust architecture
- Added hardware security key support""",
                "extracted_facts": [
                    "Company has SOC 2 Type II certification",
                    "Data encrypted with AES-256 at rest",
                    "Incident response SLA is 1 hour",
                    "Penetration testing done quarterly",
                    "Zero-trust architecture implemented",
                ],
                "comparisons": {},
            },
            {
                "id": "doc_competitor_intel",
                "title": "Competitive Intelligence Report",
                "type": "analysis",
                "author": "Strategy Team",
                "created_at": (datetime.now() - timedelta(days=14)).isoformat(),
                "updated_at": (datetime.now() - timedelta(days=7)).isoformat(),
                "tags": ["competitive", "intelligence", "strategy"],
                "content": """Competitive Intelligence Report

Key Competitors Analysis:

TechCorp (Market Leader):
- Market share: 25%
- Strengths: Brand recognition, enterprise relationships
- Weaknesses: Legacy architecture, slow innovation
- Recent moves: Acquired AI startup for $200M

InnovateSoft (#2):
- Market share: 18%
- Strengths: Modern platform, strong AI features
- Weaknesses: Limited enterprise experience
- Recent moves: Launched aggressive pricing campaign

Our Position (#3):
- Market share: 12%
- Strengths: Customer satisfaction, product reliability
- Weaknesses: Brand awareness, AI capabilities gap
- Opportunity: Underserved mid-market segment

Threat Assessment:
- TechCorp acquisition may accelerate their AI roadmap
- InnovateSoft pricing could impact SMB segment
- New entrants emerging in specific verticals

Recommendations:
1. Accelerate AI feature development
2. Strengthen mid-market positioning
3. Invest in brand awareness
4. Consider strategic partnerships""",
                "extracted_facts": [
                    "TechCorp leads with 25% market share",
                    "InnovateSoft has 18% market share with strong AI",
                    "Company is #3 with 12% market share",
                    "TechCorp acquired AI startup for $200M",
                    "Mid-market segment is underserved opportunity",
                ],
                "comparisons": {
                    "doc_market_analysis": {
                        "similarities": [
                            "Both identify competitive pressures and AI importance"
                        ],
                        "differences": [
                            "Intel report is competitor-focused, market analysis is broader"
                        ],
                        "contradictions": [],
                    }
                },
            },
        ]

        research_data = {
            "documents": documents,
            "notes": [],
            "summaries": [],
        }

        set_research_data(research_data)

        # Store in environment state
        self._state["documents"] = documents
        self._state["notes"] = []
        self._state["summaries"] = []

    def reset(self) -> None:
        """Reset the environment."""
        super().reset()
        self._setup_default_state()

    def add_document(self, document: Dict[str, Any]) -> None:
        """Add a document to the environment."""
        documents = self._state.get("documents", [])
        documents.append(document)
        self.set_state("documents", documents, source_tool="test_setup")

        research_data = get_research_data()
        research_data["documents"] = documents
        set_research_data(research_data)

    def sync_state_from_research(self) -> None:
        """Sync environment state from research data."""
        research_data = get_research_data()
        self._state["notes"] = research_data.get("notes", [])
        self._state["summaries"] = research_data.get("summaries", [])

    @property
    def document_count(self) -> int:
        """Number of documents available."""
        return len(self._state.get("documents", []))

    @property
    def note_count(self) -> int:
        """Number of research notes taken."""
        return len(self._state.get("notes", []))

    @property
    def summary_count(self) -> int:
        """Number of summaries generated."""
        return len(self._state.get("summaries", []))
