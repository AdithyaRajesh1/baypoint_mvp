# Bay Point Investment Deal Multi-Agent Pipeline MVP

A multi-agent pipeline application that analyzes investment deal documents and generates comprehensive reports on pros, cons, and final recommendations.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Create a `.env` file in the root directory:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Run the Application**:

   **Quick Start (Direct Mode)**
   
   The application can run in direct mode without external agents (uses OpenAI directly):
   ```bash
   python app.py
   ```
   
   The application will be available at `http://localhost:5001` (default port changed to avoid macOS AirPlay conflict)
   - **Web Interface**: Open `http://localhost:5001` in your browser
   
   **Recommended Mode (External Agent Services)**
   
   First, start all agents in separate terminal windows:
   
   ```bash
   # Terminal 1 - Real Estate Analysis Agent
   cd agents
   python real_estate_analysis_agent.py
   
   # Terminal 2 - Financial Modeling Agent
   cd agents
   python financial_modeling_agent.py
   
   # Terminal 3 - Market Analysis Agent
   cd agents
   python market_analysis_agent.py
   
   # Terminal 4 - Legal Analysis Agent
   cd agents
   python legal_agent.py
   ```
   ```bash
   python app.py
   ```
   
   **Note**: The application will automatically fall back to direct mode if external agents are unavailable.
   
   To use a different port for the main app, set the `PORT` environment variable:
   ```bash
   PORT=5000 python app.py
   ```
   
## Project Structure

```
baypoint_mvp/
├── app.py                 # Main Flask application
├── investment_pipeline.py  # Multi-agent analysis pipeline
├── file_processor.py      # File processing utilities
├── requirements.txt      # Python dependencies
├── agents/               # Agent service implementations
│   ├── real_estate_analysis_agent.py
│   ├── financial_modeling_agent.py
│   ├── market_analysis_agent.py
│   ├── legal_agent.py
│   └── README.md
├── static/               # Frontend files
│   ├── index.html       # Main HTML page
│   ├── style.css        # Stylesheet
│   └── script.js        # Frontend JavaScript
├── uploads/             # Uploaded files (created automatically)
└── reports/             # Generated reports (created automatically)
```

## How It Works

1. **File Upload**: User uploads an investment deal document
2. **File Processing**: Document is processed and text is extracted
3. **Multi-Agent Analysis**: 
   - Real Estate Agent analyzes property fundamentals
   - Financial Modeling Agent performs valuation and cash flow analysis
   - Market Analysis Agent evaluates location and market conditions
   - Legal Agent reviews compliance, zoning, and legal risks
   ![Multi-Agent Analysis Pipeline](./screenshots/Screenshot 2025-11-22 at 11.48.06 AM.png)
   
4. **Orchestration**: Main agent synthesizes all analyses
5. **Report Generation**: All reports are saved and returned to the user

## Agent Architecture

The pipeline supports two modes of operation:

### Direct Mode (Default)
- Uses OpenAI directly with specialized system prompts
- No external services required
- System prompts replicate agent functionality
- Simpler setup, good for development

### External Agent Mode
- Calls actual agent services via python_a2a framework
- Requires agent services to be running separately
- More scalable and modular
- Set `USE_EXTERNAL_AGENTS=true` to enable

To run in external agent mode:
1. Start each agent service in separate terminals:
   ```bash
   python agents/real_estate_analysis_agent.py
   python agents/financial_modeling_agent.py
   python agents/market_analysis_agent.py
   python agents/legal_agent.py
   ```
2. Set `USE_EXTERNAL_AGENTS=true` in your `.env` file
3. The pipeline will automatically connect to agent services
4. Falls back to direct mode if agents are unavailable

## Notes

- Maximum file size: 16MB
- Supported file formats: TXT, PDF, DOC, DOCX, MD
- Reports are saved in the `reports/` directory
- Uploaded files are saved in the `uploads/` directory

