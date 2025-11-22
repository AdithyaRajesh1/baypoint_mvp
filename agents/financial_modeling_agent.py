from python_a2a import A2AServer, skill, agent, run_server, TaskStatus, TaskState
import os
from flask import Flask, jsonify
from openai import OpenAI

@agent(
    name="Financial Modeling Agent",
    description="Performs financial modeling, valuation, and cash flow analysis for real estate investment deals",
    version="1.0.0"
)
class FinancialModelingAgent(A2AServer):
    
    def __init__(self, url=None):
        # Get port from environment or use default
        port = int(os.environ.get("PORT", 5006))
        if url is None:
            url = f"http://localhost:{port}"
        super().__init__(url=url)
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
                "agent": "Financial Modeling Agent",
                "version": "1.0.0"
            })
    
    @skill(
        name="Financial Modeling and Valuation",
        description="Performs comprehensive financial modeling including DCF analysis, IRR calculations, cash flow projections, and valuation for real estate deals",
        tags=["financial", "modeling", "valuation", "dcf", "irr", "cash-flow"]
    )
    def perform_financial_modeling(self, deal_document: str):
        """Perform financial modeling and valuation analysis for real estate deals."""
        if not self.client:
            return "OpenAI API key not set. Please set OPENAI_API_KEY in your environment."
        
        system_prompt = """You are a specialized financial modeling and valuation expert for real estate investments. Your expertise includes:

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

5. Fee Structure Analysis:
   - Management fees
   - Acquisition fees
   - Disposition fees
   - Performance fees/carried interest
   - Operating expense ratios

6. Risk-Adjusted Analysis:
   - Probability-weighted returns
   - Risk-adjusted discount rates
   - Stress testing scenarios
   - Monte Carlo simulations (conceptual)

IMPORTANT: Return your response as plain text only. Do NOT use markdown formatting such as:
- No markdown headers (###, ##, #)
- No horizontal rules (---)
- No markdown bold (**text**) or italic (*text*)
- No code blocks or backticks
- Use plain text with line breaks and simple formatting only
- Use numbered lists and bullet points with plain text (1., 2., -)

Provide detailed financial analysis with calculations, assumptions, and clear explanations of methodologies used."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Perform financial modeling and valuation analysis for the following real estate investment deal:\n\n{deal_document}"}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error performing financial modeling: {str(e)}"
    
    def handle_task(self, task):
        """Handle incoming financial modeling tasks."""
        message_data = task.message or {}
        content = message_data.get("content", {})
        text = content.get("text", "") if isinstance(content, dict) else str(content) if not isinstance(content, dict) else ""
        
        # Perform financial modeling
        analysis = self.perform_financial_modeling(text)
        
        task.artifacts = [{
            "parts": [{"type": "text", "text": analysis}]
        }]
        task.status = TaskStatus(state=TaskState.COMPLETED)
        return task

# Run the server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5006))
    url = f"http://localhost:{port}"
    agent = FinancialModelingAgent(url=url)
    print(f"Starting Financial Modeling Agent on port {port}")
    print(f"Health check available at: http://localhost:{port}/health")
    run_server(agent, host="0.0.0.0", port=port)

