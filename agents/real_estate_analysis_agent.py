from python_a2a import A2AServer, skill, agent, run_server, TaskStatus, TaskState
import os
from flask import Flask, jsonify
from openai import OpenAI

@agent(
    name="Real Estate Analysis Agent",
    description="Analyzes real estate investment deals focusing on property fundamentals, location, and operational metrics",
    version="1.0.0"
)
class RealEstateAnalysisAgent(A2AServer):
    
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
                "agent": "Real Estate Analysis Agent",
                "version": "1.0.0"
            })
    
    @skill(
        name="Analyze Property Fundamentals",
        description="Analyzes real estate property fundamentals including location, quality, occupancy, cap rates, NOI, and cash-on-cash returns",
        tags=["real-estate", "property", "analysis", "fundamentals"]
    )
    def analyze_property_fundamentals(self, deal_document: str):
        """Analyze real estate property fundamentals from deal documents."""
        if not self.client:
            return "OpenAI API key not set. Please set OPENAI_API_KEY in your environment."
        
        system_prompt = """You are a specialized real estate investment analysis agent. Your expertise includes:

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

4. Market Analysis:
   - Comparable properties (comps)
   - Market rent vs. actual rent
   - Absorption rates
   - Supply and demand dynamics
   - Market growth trends

Provide a comprehensive analysis in a structured format with clear sections."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze the following real estate investment deal:\n\n{deal_document}"}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error analyzing property fundamentals: {str(e)}"
    
    def handle_task(self, task):
        """Handle incoming analysis tasks."""
        message_data = task.message or {}
        content = message_data.get("content", {})
        text = content.get("text", "") if isinstance(content, dict) else str(content) if not isinstance(content, dict) else ""
        
        # Analyze the real estate deal
        analysis = self.analyze_property_fundamentals(text)
        
        task.artifacts = [{
            "parts": [{"type": "text", "text": analysis}]
        }]
        task.status = TaskStatus(state=TaskState.COMPLETED)
        return task

# Run the server
if __name__ == "__main__":
    agent = RealEstateAnalysisAgent()
    port = int(os.environ.get("PORT", 5005))
    print(f"Starting Real Estate Analysis Agent on port {port}")
    print(f"Health check available at: http://localhost:{port}/health")
    run_server(agent, host="0.0.0.0", port=port)

