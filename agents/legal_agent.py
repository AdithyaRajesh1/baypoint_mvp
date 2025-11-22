from python_a2a import A2AServer, skill, agent, run_server, TaskStatus, TaskState
import os
from flask import Flask, jsonify
from openai import OpenAI

@agent(
    name="Legal Analysis Agent",
    description="Analyzes legal structure, regulatory compliance, zoning, title, and legal risks for real estate investment deals",
    version="1.0.0"
)
class LegalAgent(A2AServer):
    
    def __init__(self, url=None):
        # Get port from environment or use default
        port = int(os.environ.get("PORT", 5008))
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
                "agent": "Legal Analysis Agent",
                "version": "1.0.0"
            })
    
    @skill(
        name="Legal and Regulatory Analysis",
        description="Analyzes legal structure, regulatory compliance, zoning, title issues, environmental regulations, and legal risks for real estate deals",
        tags=["legal", "compliance", "regulatory", "zoning", "title", "environmental"]
    )
    def analyze_legal_aspects(self, deal_document: str):
        """Analyze legal, regulatory, and compliance aspects of real estate deals."""
        if not self.client:
            return "OpenAI API key not set. Please set OPENAI_API_KEY in your environment."
        
        system_prompt = """You are a specialized real estate legal and regulatory compliance expert. Your expertise includes:

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
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze the legal, regulatory, and compliance aspects of the following real estate investment deal:\n\n{deal_document}"}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error analyzing legal aspects: {str(e)}"
    
    def handle_task(self, task):
        """Handle incoming legal analysis tasks."""
        message_data = task.message or {}
        content = message_data.get("content", {})
        text = content.get("text", "") if isinstance(content, dict) else str(content) if not isinstance(content, dict) else ""
        
        # Analyze the legal aspects
        analysis = self.analyze_legal_aspects(text)
        
        task.artifacts = [{
            "parts": [{"type": "text", "text": analysis}]
        }]
        task.status = TaskStatus(state=TaskState.COMPLETED)
        return task

# Run the server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5008))
    url = f"http://localhost:{port}"
    agent = LegalAgent(url=url)
    print(f"Starting Legal Analysis Agent on port {port}")
    print(f"Health check available at: http://localhost:{port}/health")
    run_server(agent, host="0.0.0.0", port=port)

