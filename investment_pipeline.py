from openai import OpenAI
import os
from file_processor import FileProcessor
import requests

class InvestmentAnalysisPipeline:
    """
    Multi-agent pipeline for analyzing investment deals.
    Uses specialized agents for real estate analysis, financial modeling, market analysis, and final synthesis.
    """
    
    def __init__(self):
        self.setup_agents()
        self.file_processor = FileProcessor()
        # Agent endpoints (can be configured via environment variables)
        self.real_estate_agent_url = os.environ.get("REAL_ESTATE_AGENT_URL", "http://localhost:5005")
        self.financial_modeling_agent_url = os.environ.get("FINANCIAL_MODELING_AGENT_URL", "http://localhost:5006")
        self.market_analysis_agent_url = os.environ.get("MARKET_ANALYSIS_AGENT_URL", "http://localhost:5007")
        self.use_external_agents = os.environ.get("USE_EXTERNAL_AGENTS", "false").lower() == "true"
    
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

Provide a comprehensive analysis in a structured format with clear sections."""
        
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

Provide comprehensive market analysis with data-driven insights and clear risk/opportunity assessments."""
        
        # Orchestrator/Synthesis Agent System Prompt
        self.orchestrator_system_prompt = """You are a senior investment analyst and orchestrator responsible for synthesizing multiple specialized analyses into a comprehensive final investment recommendation report.

Your role is to:
1. Review and synthesize all specialized agent analyses (real estate fundamentals, financial modeling, market analysis)
2. Provide a balanced, professional investment recommendation
3. Create a comprehensive final report that includes:
   - Executive Summary
   - Deal Overview
   - Real Estate Fundamentals Summary
   - Financial Analysis Summary
   - Market Analysis Summary
   - Investment Recommendation (Invest / Do Not Invest / Conditional)
   - Key Decision Factors
   - Risk Assessment
   - Next Steps and Action Items

Be professional, balanced, and provide actionable insights. Your recommendation should be clear and well-justified based on all the analyses provided."""
    
    def _call_external_agent(self, agent_url, deal_content):
        """Call an external agent via HTTP if available"""
        try:
            # This would use python_a2a client in production
            # For now, we'll use OpenAI directly with specialized prompts
            return None
        except Exception as e:
            print(f"Warning: Could not reach external agent at {agent_url}: {e}")
            return None
    
    def analyze(self, filepath):
        """
        Main analysis pipeline that processes the investment deal file through all agents.
        
        Args:
            filepath: Path to the investment deal document
            
        Returns:
            Dictionary containing reports from all agents and orchestrator
        """
        # Step 1: Process and extract text from file
        print("📄 Processing investment deal document...")
        deal_content = self.file_processor.process_file(filepath)
        
        if not deal_content:
            raise ValueError("Failed to extract content from the investment deal file")
        
        # Step 2: Real Estate Analysis Agent
        print("🏢 Running Real Estate Analysis Agent...")
        real_estate_prompt = f"""Analyze the following real estate investment deal document:

{deal_content}

Provide a comprehensive analysis of property fundamentals, financial metrics, and operational metrics."""
        
        real_estate_response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self.real_estate_system_prompt},
                {"role": "user", "content": real_estate_prompt}
            ],
            temperature=0.7
        )
        real_estate_report = real_estate_response.choices[0].message.content
        
        # Step 3: Financial Modeling Agent
        print("💰 Running Financial Modeling Agent...")
        financial_prompt = f"""Perform financial modeling and valuation analysis for the following real estate investment deal:

{deal_content}

Provide detailed financial analysis including DCF, IRR, cash flow projections, and valuation."""
        
        financial_response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self.financial_modeling_system_prompt},
                {"role": "user", "content": financial_prompt}
            ],
            temperature=0.7
        )
        financial_report = financial_response.choices[0].message.content
        
        # Step 4: Market Analysis Agent
        print("📊 Running Market Analysis Agent...")
        market_prompt = f"""Analyze the market, location, and comparable properties for the following real estate investment deal:

{deal_content}

Provide comprehensive market analysis including location quality, market trends, and comparable properties."""
        
        market_response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self.market_analysis_system_prompt},
                {"role": "user", "content": market_prompt}
            ],
            temperature=0.7
        )
        market_report = market_response.choices[0].message.content
        
        # Step 5: Orchestrator/Synthesis Agent
        print("🎯 Running Orchestrator Agent...")
        orchestrator_prompt = f"""Synthesize the following specialized analyses into a comprehensive final investment recommendation:

ORIGINAL DEAL DOCUMENT:
{deal_content}

REAL ESTATE FUNDAMENTALS ANALYSIS:
{real_estate_report}

FINANCIAL MODELING ANALYSIS:
{financial_report}

MARKET ANALYSIS:
{market_report}

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
        
        print("✅ Analysis complete!")
        
        return {
            "real_estate_report": real_estate_report,
            "financial_modeling_report": financial_report,
            "market_analysis_report": market_report,
            "orchestrator_report": orchestrator_report
        }

