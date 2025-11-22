from openai import OpenAI
import os
from file_processor import FileProcessor
import requests
from python_a2a import AgentNetwork, Message, TextContent, MessageRole

class InvestmentAnalysisPipeline:
    """
    Multi-agent pipeline for analyzing investment deals.
    Uses specialized agents for real estate analysis, financial modeling, market analysis, legal analysis, and final synthesis.
    
    The pipeline can operate in two modes:
    1. External Agent Mode (USE_EXTERNAL_AGENTS=true): Calls actual agent services via python_a2a
       - Requires agent services to be running on configured ports
       - Falls back to direct OpenAI calls if agents are unavailable
    2. Direct Mode (default): Uses OpenAI directly with specialized system prompts
       - No external services required
       - System prompts replicate agent functionality
    """
    
    def __init__(self):
        self.setup_agents()
        self.file_processor = FileProcessor()
        # Agent endpoints (can be configured via environment variables)
        self.real_estate_agent_url = os.environ.get("REAL_ESTATE_AGENT_URL", "http://localhost:5005")
        self.financial_modeling_agent_url = os.environ.get("FINANCIAL_MODELING_AGENT_URL", "http://localhost:5006")
        self.market_analysis_agent_url = os.environ.get("MARKET_ANALYSIS_AGENT_URL", "http://localhost:5007")
        self.legal_agent_url = os.environ.get("LEGAL_AGENT_URL", "http://localhost:5008")
        self.use_external_agents = os.environ.get("USE_EXTERNAL_AGENTS", "false").lower() == "true"
        
        # Initialize agent network if using external agents
        if self.use_external_agents:
            self.agent_network = AgentNetwork()
            try:
                self.agent_network.add("real_estate", self.real_estate_agent_url)
                self.agent_network.add("financial_modeling", self.financial_modeling_agent_url)
                self.agent_network.add("market_analysis", self.market_analysis_agent_url)
                self.agent_network.add("legal", self.legal_agent_url)
                print("Connected to external agent services")
            except Exception as e:
                print(f"Warning: Could not connect to external agents: {e}")
                print("   Falling back to direct OpenAI calls with system prompts")
                self.use_external_agents = False
        else:
            self.agent_network = None
    
    def setup_agents(self):
        """Initialize the agent configurations with specialized investment analysis prompts"""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=api_key)
        
        # Real Estate Analysis Agent System Prompt
        self.real_estate_system_prompt = """You are a specialized real estate investment analysis agent. Your expertise includes:

1. Property Fundamentals Analysis:
   - Location quality and desirability
   - Property type and quality (Class A, B, C)
   - Physical condition and age
   - Zoning and land use restrictions
   - Environmental considerations

2. Financial Metrics:
   - Cap rates and capitalization rates
   - Net Operating Income (NOI) analysis
   - Cash-on-cash returns
   - Gross Rental Multiplier (GRM)
   - Debt Service Coverage Ratio (DSCR)
   - Loan-to-Value (LTV) ratios

3. Operational Metrics:
   - Occupancy rates and trends
   - Lease terms and tenant quality
   - Property management quality
   - Operating expenses and expense ratios
   - Maintenance and capital expenditure needs

IMPORTANT: Return your response as plain text only. Do NOT use markdown formatting such as:
- No markdown headers (###, ##, #)
- No horizontal rules (---)
- No markdown bold (**text**) or italic (*text*)
- No code blocks or backticks
- Use plain text with line breaks and simple formatting only
- Use numbered lists and bullet points with plain text (1., 2., -)

Provide a comprehensive analysis in a structured format with clear sections using plain text only."""
        
        # Financial Modeling Agent System Prompt
        self.financial_modeling_system_prompt = """You are a specialized financial modeling and valuation expert for real estate investments. Your expertise includes:

1. Financial Modeling:
   - Discounted Cash Flow (DCF) analysis
   - Pro forma income statements
   - Cash flow projections (5-10 year horizons)
   - Sensitivity analysis and scenario modeling
   - Break-even analysis

2. Return Metrics:
   - Internal Rate of Return (IRR) calculations
   - Multiple on Invested Capital (MOIC)
   - Equity Multiple
   - Cash-on-Cash Return
   - Net Present Value (NPV)
   - Yield analysis

3. Valuation Methods:
   - Income approach (capitalization method)
   - Sales comparison approach
   - Cost approach
   - Discounted cash flow valuation
   - Terminal value calculations

4. Capital Structure Analysis:
   - Debt vs. equity financing
   - Loan terms and amortization schedules
   - Interest rate analysis
   - Leverage impact on returns
   - Refinancing scenarios

IMPORTANT: Return your response as plain text only. Do NOT use markdown formatting such as:
- No markdown headers (###, ##, #)
- No horizontal rules (---)
- No markdown bold (**text**) or italic (*text*)
- No code blocks or backticks
- Use plain text with line breaks and simple formatting only
- Use numbered lists and bullet points with plain text (1., 2., -)

Provide detailed financial analysis with calculations, assumptions, and clear explanations of methodologies used."""
        
        # Market Analysis Agent System Prompt
        self.market_analysis_system_prompt = """You are a specialized real estate market analysis expert. Your expertise includes:

1. Location Analysis:
   - Neighborhood quality and desirability
   - Demographics and population trends
   - Economic indicators (employment, income growth)
   - School district quality
   - Crime rates and safety
   - Walkability and transit access
   - Proximity to amenities
   - Future development plans and infrastructure projects

2. Market Trends:
   - Historical price appreciation trends
   - Rental rate trends and forecasts
   - Occupancy trends
   - Absorption rates
   - Days on market (DOM) trends
   - Market cycle position

3. Supply and Demand Dynamics:
   - Current inventory levels
   - New construction pipeline
   - Absorption rates
   - Vacancy rates and trends
   - Population growth and migration patterns
   - Job growth and economic development

4. Comparable Properties (Comps):
   - Similar properties in the area
   - Recent sales comparables
   - Rental comparables
   - Price per square foot analysis
   - Cap rate comparables
   - Feature comparisons

5. Competitive Landscape:
   - Competing properties
   - Market positioning
   - Competitive advantages/disadvantages
   - Market share analysis

IMPORTANT: Return your response as plain text only. Do NOT use markdown formatting such as:
- No markdown headers (###, ##, #)
- No horizontal rules (---)
- No markdown bold (**text**) or italic (*text*)
- No code blocks or backticks
- Use plain text with line breaks and simple formatting only
- Use numbered lists and bullet points with plain text (1., 2., -)

Provide comprehensive market analysis with data-driven insights and clear risk/opportunity assessments."""
        
        # Legal Analysis Agent System Prompt
        self.legal_system_prompt = """You are a specialized real estate legal and regulatory compliance expert. Your expertise includes:

1. Legal Structure Analysis:
   - Entity types (LLC, LP, Corporation, Trust)
   - Ownership structure and beneficial ownership
   - Partnership agreements and operating agreements
   - Corporate governance requirements
   - Legal entity formation and jurisdiction

2. Regulatory Compliance:
   - SEC regulations (if applicable for investment funds)
   - State and local real estate regulations
   - Fair housing laws and compliance
   - Americans with Disabilities Act (ADA) compliance
   - Building codes and safety regulations
   - Fire safety and life safety codes

3. Zoning and Land Use:
   - Current zoning classification
   - Permitted uses and restrictions
   - Variance requirements and special permits
   - Setback requirements
   - Density restrictions
   - Future zoning changes and development plans
   - Non-conforming use issues

4. Title and Ownership:
   - Title insurance and title defects
   - Easements and encumbrances
   - Liens and judgments
   - Boundary disputes
   - Mineral rights and subsurface rights
   - Air rights and development rights
   - Condemnation and eminent domain risks

5. Environmental Regulations:
   - Environmental site assessments (Phase I/II)
   - Contaminated land issues
   - Asbestos and lead-based paint
   - Wetlands and protected areas
   - Endangered species considerations
   - Stormwater management requirements
   - Brownfield redevelopment programs

6. Contract and Lease Review:
   - Purchase and sale agreements
   - Lease agreements and terms
   - Assignment and subletting rights
   - Default and termination provisions
   - Dispute resolution mechanisms
   - Force majeure clauses

7. Tax and Structuring:
   - Property tax assessments
   - Transfer tax implications
   - 1031 exchange opportunities
   - Tax abatements and incentives
   - Entity-level tax considerations
   - State and local tax implications

8. Due Diligence Legal Issues:
   - Permits and approvals
   - Violations and citations
   - Pending litigation
   - Regulatory enforcement actions
   - Insurance claims history
   - Historical compliance issues

9. Risk Assessment:
   - Legal liability exposure
   - Regulatory enforcement risks
   - Litigation risks
   - Compliance failure consequences
   - Reputation risks

IMPORTANT: Return your response as plain text only. Do NOT use markdown formatting such as:
- No markdown headers (###, ##, #)
- No horizontal rules (---)
- No markdown bold (**text**) or italic (*text*)
- No code blocks or backticks
- Use plain text with line breaks and simple formatting only
- Use numbered lists and bullet points with plain text (1., 2., -)

Provide comprehensive legal analysis with clear identification of risks, compliance requirements, and recommended actions. Structure your response with clear sections for each area of analysis."""
        
        # Orchestrator/Synthesis Agent System Prompt
        self.orchestrator_system_prompt = """You are a senior investment analyst and orchestrator responsible for synthesizing multiple specialized analyses into a comprehensive final investment recommendation report.

Your role is to:
1. Review and synthesize all specialized agent analyses (real estate fundamentals, financial modeling, market analysis, legal/compliance)
2. Provide a balanced, professional investment recommendation
3. Create a comprehensive final report that includes:
   - Executive Summary
   - Deal Overview
   - Real Estate Fundamentals Summary
   - Financial Analysis Summary
   - Market Analysis Summary
   - Legal and Compliance Summary
   - Investment Recommendation (Invest / Do Not Invest / Conditional)
   - Key Decision Factors
   - Risk Assessment (including legal risks)
   - Next Steps and Action Items

IMPORTANT: Return your response as plain text only. Do NOT use markdown formatting such as:
- No markdown headers (###, ##, #)
- No horizontal rules (---)
- No markdown bold (**text**) or italic (*text*)
- No code blocks or backticks
- Use plain text with line breaks and simple formatting only
- Use numbered lists and bullet points with plain text (1., 2., -)

Be professional, balanced, and provide actionable insights. Your recommendation should be clear and well-justified based on all the analyses provided."""
    
    def _call_agent(self, agent_id, deal_content, system_prompt, user_prompt):
        """
        Call an agent either via external service or using OpenAI directly.
        
        Args:
            agent_id: ID of the agent (real_estate, financial_modeling, market_analysis, legal)
            deal_content: The deal document content
            system_prompt: System prompt for direct OpenAI call (fallback)
            user_prompt: User prompt for the analysis
            
        Returns:
            Agent response as string
        """
        # Try external agent first if enabled
        if self.use_external_agents and self.agent_network:
            try:
                agent = self.agent_network.get_agent(agent_id)
                message = Message(
                    content=TextContent(text=user_prompt),
                    role=MessageRole.USER
                )
                response = agent.ask(message)
                # Extract text from response
                if isinstance(response, str):
                    return response
                elif hasattr(response, 'content'):
                    if isinstance(response.content, list):
                        return "\n".join([item.text if hasattr(item, 'text') else str(item) for item in response.content])
                    elif hasattr(response.content, 'text'):
                        return response.content.text
                return str(response)
            except Exception as e:
                print(f"Warning: Could not reach {agent_id} agent service: {e}")
                print(f"   Falling back to direct OpenAI call")
        
        # Fallback to direct OpenAI call with system prompt
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error calling {agent_id} agent: {str(e)}")
    
    def analyze(self, filepath):
        """
        Main analysis pipeline that processes the investment deal file through all agents.
        
        Args:
            filepath: Path to the investment deal document
            
        Returns:
            Dictionary containing reports from all agents and orchestrator
        """
        # Step 1: Process and extract text from file
        print("Processing investment deal document...")
        deal_content = self.file_processor.process_file(filepath)
        
        if not deal_content:
            raise ValueError("Failed to extract content from the investment deal file")
        
        # Step 2: Real Estate Analysis Agent
        print("Running Real Estate Analysis Agent...")
        real_estate_prompt = f"""Analyze the following real estate investment deal document:

{deal_content}

Provide a comprehensive analysis of property fundamentals, financial metrics, and operational metrics."""
        
        real_estate_report = self._call_agent(
            "real_estate",
            deal_content,
            self.real_estate_system_prompt,
            real_estate_prompt
        )
        
        # Step 3: Financial Modeling Agent
        print("Running Financial Modeling Agent...")
        financial_prompt = f"""Perform financial modeling and valuation analysis for the following real estate investment deal:

{deal_content}

Provide detailed financial analysis including DCF, IRR, cash flow projections, and valuation."""
        
        financial_report = self._call_agent(
            "financial_modeling",
            deal_content,
            self.financial_modeling_system_prompt,
            financial_prompt
        )
        
        # Step 4: Market Analysis Agent
        print("Running Market Analysis Agent...")
        market_prompt = f"""Analyze the market, location, and comparable properties for the following real estate investment deal:

{deal_content}

Provide comprehensive market analysis including location quality, market trends, and comparable properties."""
        
        market_report = self._call_agent(
            "market_analysis",
            deal_content,
            self.market_analysis_system_prompt,
            market_prompt
        )
        
        # Step 5: Legal Analysis Agent
        print("Running Legal Analysis Agent...")
        legal_prompt = f"""Analyze the legal, regulatory, and compliance aspects of the following real estate investment deal:

{deal_content}

Provide comprehensive legal analysis including structure, compliance, zoning, title, and legal risks."""
        
        legal_report = self._call_agent(
            "legal",
            deal_content,
            self.legal_system_prompt,
            legal_prompt
        )
        
        # Step 6: Orchestrator/Synthesis Agent
        print("Running Orchestrator Agent...")
        orchestrator_prompt = f"""Synthesize the following specialized analyses into a comprehensive final investment recommendation:

ORIGINAL DEAL DOCUMENT:
{deal_content}

REAL ESTATE FUNDAMENTALS ANALYSIS:
{real_estate_report}

FINANCIAL MODELING ANALYSIS:
{financial_report}

MARKET ANALYSIS:
{market_report}

LEGAL AND COMPLIANCE ANALYSIS:
{legal_report}

Create a comprehensive final report with a clear investment recommendation based on all analyses."""
        
        orchestrator_response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self.orchestrator_system_prompt},
                {"role": "user", "content": orchestrator_prompt}
            ],
            temperature=0.7
        )
        orchestrator_report = orchestrator_response.choices[0].message.content
        
        print("Analysis complete!")
        
        return {
            "real_estate_report": real_estate_report,
            "financial_modeling_report": financial_report,
            "market_analysis_report": market_report,
            "legal_report": legal_report,
            "orchestrator_report": orchestrator_report
        }

