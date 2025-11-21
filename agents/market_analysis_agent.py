from python_a2a import A2AServer, skill, agent, run_server, TaskStatus, TaskState
import os
from flask import Flask, jsonify
from openai import OpenAI

@agent(
    name="Market Analysis Agent",
    description="Analyzes real estate markets, location dynamics, comparable properties, and market trends for investment deals",
    version="1.0.0"
)
class MarketAnalysisAgent(A2AServer):
    
    def __init__(self):
        super().__init__()
        self.app = Flask(__name__)
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None
        
        @self.app.route('/health')
        def health_check():
            return jsonify({
                "status": "healthy",
                "agent": "Market Analysis Agent",
                "version": "1.0.0"
            })
    
    @skill(
        name="Market and Location Analysis",
        description="Analyzes real estate markets, location quality, comparable properties, market trends, and supply/demand dynamics",
        tags=["market", "location", "comps", "trends", "analysis"]
    )
    def analyze_market(self, deal_document: str):
        """Analyze market conditions, location, and comparable properties for real estate deals."""
        if not self.client:
            return "OpenAI API key not set. Please set OPENAI_API_KEY in your environment."
        
        system_prompt = """You are a specialized real estate market analysis expert. Your expertise includes:

1. Location Analysis:
   - Neighborhood quality and desirability
   - Demographics and population trends
   - Economic indicators (employment, income growth)
   - School district quality
   - Crime rates and safety
   - Walkability and transit access
   - Proximity to amenities (shopping, dining, entertainment)
   - Future development plans and infrastructure projects

2. Market Trends:
   - Historical price appreciation trends
   - Rental rate trends and forecasts
   - Occupancy trends
   - Absorption rates
   - Days on market (DOM) trends
   - Market cycle position (expansion, peak, contraction, recovery)

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
   - Differentiation factors

6. Macroeconomic Factors:
   - Interest rate environment
   - Inflation impact
   - Economic growth indicators
   - Real estate market cycles
   - Regional economic health

7. Risk Factors:
   - Market saturation risks
   - Economic downturn risks
   - Regulatory changes
   - Environmental risks
   - Gentrification or decline risks

Provide comprehensive market analysis with data-driven insights and clear risk/opportunity assessments."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze the market, location, and comparable properties for the following real estate investment deal:\n\n{deal_document}"}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error analyzing market: {str(e)}"
    
    def handle_task(self, task):
        """Handle incoming market analysis tasks."""
        message_data = task.message or {}
        content = message_data.get("content", {})
        text = content.get("text", "") if isinstance(content, dict) else str(content) if not isinstance(content, dict) else ""
        
        # Analyze the market
        analysis = self.analyze_market(text)
        
        task.artifacts = [{
            "parts": [{"type": "text", "text": analysis}]
        }]
        task.status = TaskStatus(state=TaskState.COMPLETED)
        return task

# Run the server
if __name__ == "__main__":
    agent = MarketAnalysisAgent()
    port = int(os.environ.get("PORT", 5007))
    print(f"Starting Market Analysis Agent on port {port}")
    print(f"Health check available at: http://localhost:{port}/health")
    run_server(agent, host="0.0.0.0", port=port)

