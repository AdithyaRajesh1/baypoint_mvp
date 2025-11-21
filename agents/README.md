# Real Estate Investment Deal Agents

This directory contains specialized agents for analyzing real estate investment deals using the python_a2a framework.

## Agents

### 1. Real Estate Analysis Agent (Port 5005)
**File**: `real_estate_analysis_agent.py`

Analyzes property fundamentals including:
- Property quality and condition
- Cap rates and NOI
- Occupancy and tenant quality
- Operating expenses
- Property management

**Usage**:
```bash
python agents/real_estate_analysis_agent.py
```

### 2. Financial Modeling Agent (Port 5006)
**File**: `financial_modeling_agent.py`

Performs financial modeling and valuation:
- DCF analysis
- IRR and MOIC calculations
- Cash flow projections
- Valuation methodologies
- Capital structure analysis

**Usage**:
```bash
python agents/financial_modeling_agent.py
```

### 3. Market Analysis Agent (Port 5007)
**File**: `market_analysis_agent.py`

Analyzes market conditions and location:
- Location quality and demographics
- Market trends and cycles
- Comparable properties (comps)
- Supply and demand dynamics
- Competitive landscape

**Usage**:
```bash
python agents/market_analysis_agent.py
```

## Setup

1. **Install Dependencies**:
   ```bash
   pip install python_a2a openai flask httpx
   ```

2. **Set Environment Variables**:
   ```bash
   export OPENAI_API_KEY=your_openai_api_key
   export PORT=5005  # or 5006, 5007 for different agents
   ```

3. **Run Agents**:
   Each agent runs as a separate server. You can run them in separate terminals or use a process manager.

## Integration with Main Pipeline

These agents can be integrated into your main `investment_pipeline.py` by:

1. Adding them to the `AgentNetwork`:
   ```python
   network.add("real_estate_agent", "http://localhost:5005")
   network.add("financial_modeling_agent", "http://localhost:5006")
   network.add("market_analysis_agent", "http://localhost:5007")
   ```

2. Routing real estate deals to these specialized agents

3. Combining their outputs in a synthesis agent

## Health Checks

Each agent provides a health check endpoint:
- Real Estate Agent: `http://localhost:5005/health`
- Financial Modeling Agent: `http://localhost:5006/health`
- Market Analysis Agent: `http://localhost:5007/health`

## Notes

- Each agent uses GPT-4o for analysis
- Agents are designed to work with real estate deal documents
- All agents follow the python_a2a framework pattern
- Agents can be deployed separately or together

