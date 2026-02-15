# TradeWizard DOA - Multi-Agent Prediction Market Analysis

A Python-based multi-agent system for analyzing prediction markets on Polymarket using specialized AI agents. Built with LangGraph and Digital Ocean's Gradient AI Platform, this system replicates TradeWizard's market intelligence capabilities within the DOA (Digital Ocean Agents) framework.

## Overview

TradeWizard DOA transforms prediction market analysis from speculative guessing into data-driven intelligence by orchestrating specialized AI agents that examine markets from multiple perspectives: market microstructure, probability baseline, risk assessment, news analysis, polling data, sentiment, price action, and event scenarios.

### Key Features

- **Multi-Agent Intelligence**: 13 specialized agents analyze markets from different perspectives
- **Parallel Execution**: Agents run concurrently using LangGraph's Send API for fast analysis
- **Debate Protocol**: Bull and bear theses are constructed and cross-examined adversarially
- **Consensus Engine**: Unified probability estimates with confidence bands and disagreement metrics
- **Memory System**: Historical context from past analyses informs agent decisions
- **Trade Recommendations**: Actionable signals with entry/target zones, expected value, and risk assessment
- **Full Observability**: Opik integration for LLM tracing, cost tracking, and performance monitoring

## Architecture

### Workflow Overview

```
Market Analysis Request (condition_id)
    ↓
[Market Ingestion] → Fetch market data from Polymarket
    ↓
[Memory Retrieval] → Load historical agent signals for context
    ↓
[Keyword Extraction] → Extract keywords from market/event data
    ↓
[Dynamic Agent Selection] → Determine which agents to activate
    ↓
[Parallel Agent Execution] → All agents analyze simultaneously
    ↓
[Agent Signal Fusion] → Aggregate signals with dynamic weighting
    ↓
[Thesis Construction] → Build bull and bear theses
    ↓
[Cross-Examination] → Test theses against each other
    ↓
[Consensus Engine] → Calculate unified probability estimate
    ↓
[Recommendation Generation] → Create actionable trade recommendation
    ↓
Trade Recommendation Output
```

### Agent Types

**MVP Agents** (always active):
- **Market Microstructure**: Analyzes order book dynamics, liquidity, and trading patterns
- **Probability Baseline**: Provides baseline probability estimates using statistical methods
- **Risk Assessment**: Identifies tail risks and potential failure scenarios

**Event Intelligence Agents**:
- **Breaking News**: Analyzes recent news developments and their market impact
- **Event Impact**: Assesses how events affect market outcomes

**Polling & Statistical Agents**:
- **Polling Intelligence**: Interprets polling data and survey results
- **Historical Pattern**: Identifies patterns from similar past events

**Sentiment & Narrative Agents**:
- **Media Sentiment**: Analyzes media coverage and narrative framing
- **Social Sentiment**: Tracks social media sentiment and discussion volume
- **Narrative Velocity**: Measures how quickly narratives are evolving

**Price Action Agents**:
- **Momentum**: Detects momentum signals and trend strength
- **Mean Reversion**: Identifies overbought/oversold conditions

**Event Scenario Agents**:
- **Catalyst**: Identifies potential catalysts that could move markets
- **Tail Risk**: Models low-probability, high-impact scenarios

## Prerequisites

- Python 3.10+
- Digital Ocean account with Gradient AI access
- Polymarket API access
- Supabase account (or local PostgreSQL)
- Opik account (optional, for observability)

## Setup

### 1. Create Virtual Environment

```bash
cd doa
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# Gradient AI Configuration
GRADIENT_ACCESS_TOKEN=your_gradient_token
GRADIENT_WORKSPACE_ID=your_workspace_id
LLM_MODEL=meta-llama/llama-3.1-70b-instruct

# Polymarket Configuration
POLYMARKET_GAMMA_API_URL=https://gamma-api.polymarket.com
POLYMARKET_CLOB_API_URL=https://clob.polymarket.com

# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Opik Configuration (optional)
OPIK_API_KEY=your_opik_key
OPIK_WORKSPACE=your_workspace
OPIK_PROJECT_NAME=tradewizard-doa

# Agent Configuration
AGENT_TIMEOUT_MS=30000
MAX_RETRIES=3
ENABLE_ADVANCED_AGENTS=true
```

### 4. Set Up Database

Run the database migrations to create required tables:

```bash
python -m database.migrations.001_initial_schema
```

Or manually execute the SQL in `database/migrations/001_initial_schema.sql` against your Supabase database.

## Usage

### CLI Commands

#### Analyze a Market

```bash
python main.py analyze <condition_id>
```

Example:
```bash
python main.py analyze 0x1234567890abcdef
```

Output:
```
🔍 Analyzing market: Will Biden win the 2024 election?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Market Data Ingested
   Current Price: 52.5¢
   Liquidity: $2.4M
   24h Volume: $156K

🧠 Memory Retrieved
   Found 3 historical analyses for this market

🤖 Agents Activated: 13 agents
   MVP: Market Microstructure, Probability Baseline, Risk Assessment
   Event Intelligence: Breaking News, Event Impact
   Polling: Polling Intelligence, Historical Pattern
   Sentiment: Media Sentiment, Social Sentiment, Narrative Velocity
   Price Action: Momentum, Mean Reversion
   Event Scenario: Catalyst, Tail Risk

⚡ Agent Signals (13/13 completed)
   ✓ Market Microstructure: YES 55% (confidence: 0.82)
   ✓ Probability Baseline: YES 53% (confidence: 0.75)
   ✓ Risk Assessment: YES 51% (confidence: 0.68)
   ... (10 more agents)

🎯 Thesis Construction
   Bull Thesis: YES at 56% (edge: 3.5%)
   Bear Thesis: NO at 48% (edge: 4.5%)

⚔️  Cross-Examination
   Bull Score: 0.65 (survived 4/5 tests)
   Bear Score: 0.45 (survived 2/5 tests)

🎲 Consensus Probability
   Consensus: 54.2% (confidence band: 51.8% - 56.6%)
   Disagreement Index: 0.12 (low)
   Regime: high-confidence

💡 Trade Recommendation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Action: LONG_YES
Entry Zone: 51.0¢ - 53.0¢
Target Zone: 56.0¢ - 58.0¢
Expected Value: +$4.20 per $100 invested
Win Probability: 62%
Liquidity Risk: low

Summary:
Strong polling fundamentals and positive media sentiment support a YES position.
The market is slightly underpricing the consensus probability, creating a 
favorable entry opportunity.

Core Thesis:
Recent polling shows consistent lead in key swing states, with improving 
favorability ratings. Media narrative has shifted positively following recent 
policy announcements.

Key Catalysts:
- Upcoming debate performance
- Q3 economic data release
- Swing state polling updates

Failure Scenarios:
- Unexpected scandal or controversy
- Economic downturn
- Third-party candidate surge

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Analysis complete in 12.4s | Cost: $0.23 | 13 agents | 47 LLM calls
```

#### Query Analysis History

```bash
python main.py history <condition_id>
```

Shows past analyses for a market with timestamps, recommendations, and outcomes.

#### Start Continuous Monitoring

```bash
python main.py monitor
```

Continuously monitors configured markets and generates alerts on significant changes.

### Programmatic Usage

```python
from main import analyze_market
from config import load_config

# Load configuration
config = load_config()

# Analyze a market
result = await analyze_market(
    condition_id="0x1234567890abcdef",
    config=config
)

# Access recommendation
print(f"Action: {result.recommendation.action}")
print(f"Entry Zone: {result.recommendation.entry_zone}")
print(f"Expected Value: ${result.recommendation.expected_value}")

# Access agent signals
for signal in result.agent_signals:
    print(f"{signal.agent_name}: {signal.direction} {signal.fair_probability}")
```

## Project Structure

```
doa/
├── agents/                 # Intelligence agent implementations
│   ├── agent_factory.py   # Factory for creating agent nodes
│   ├── market_microstructure.py
│   ├── probability_baseline.py
│   ├── risk_assessment.py
│   ├── breaking_news.py
│   ├── event_impact.py
│   ├── polling_intelligence.py
│   ├── historical_pattern.py
│   ├── media_sentiment.py
│   ├── social_sentiment.py
│   ├── narrative_velocity.py
│   ├── momentum.py
│   ├── mean_reversion.py
│   ├── catalyst.py
│   └── tail_risk.py
├── nodes/                  # LangGraph workflow nodes
│   ├── market_ingestion.py
│   ├── memory_retrieval.py
│   ├── keyword_extraction.py
│   ├── dynamic_agent_selection.py
│   ├── agent_signal_fusion.py
│   ├── thesis_construction.py
│   ├── cross_examination.py
│   ├── consensus_engine.py
│   └── recommendation_generation.py
├── models/                 # Data models and state definitions
│   ├── types.py           # Pydantic models
│   └── state.py           # LangGraph state
├── tools/                  # External integrations
│   └── polymarket_client.py
├── database/               # Persistence layer
│   ├── supabase_client.py
│   ├── persistence.py
│   ├── memory_retrieval.py
│   └── migrations/
│       └── 001_initial_schema.sql
├── utils/                  # Utilities
│   ├── llm_factory.py
│   ├── audit_logger.py
│   └── result.py
├── main.py                 # Main workflow and entry point
├── config.py               # Configuration management
├── prompts.py              # All agent prompts
├── requirements.txt
├── .env.example
└── README.md
```

## Data Models

### MarketBriefingDocument

Primary input to all intelligence agents:

```python
{
    "market_id": "0x1234...",
    "condition_id": "0xabcd...",
    "event_type": "election",
    "question": "Will Biden win the 2024 election?",
    "resolution_criteria": "Resolves YES if...",
    "expiry_timestamp": 1704067200,
    "current_probability": 0.525,
    "liquidity_score": 8.5,
    "bid_ask_spread": 0.02,
    "volatility_regime": "medium",
    "volume_24h": 156000.0
}
```

### AgentSignal

Output from individual agents:

```python
{
    "agent_name": "market_microstructure",
    "timestamp": 1704067200,
    "confidence": 0.82,
    "direction": "YES",
    "fair_probability": 0.55,
    "key_drivers": [
        "Strong bid-side liquidity",
        "Decreasing spread indicates confidence",
        "Volume surge on YES side"
    ],
    "risk_factors": [
        "Low overall liquidity could amplify moves",
        "Recent volatility suggests uncertainty"
    ],
    "metadata": {}
}
```

### TradeRecommendation

Final actionable output:

```python
{
    "market_id": "0x1234...",
    "action": "LONG_YES",
    "entry_zone": (0.51, 0.53),
    "target_zone": (0.56, 0.58),
    "expected_value": 4.20,
    "win_probability": 0.62,
    "liquidity_risk": "low",
    "explanation": {
        "summary": "Strong polling fundamentals...",
        "core_thesis": "Recent polling shows...",
        "key_catalysts": ["Upcoming debate", "Q3 data"],
        "failure_scenarios": ["Unexpected scandal", "Economic downturn"]
    },
    "metadata": {
        "consensus_probability": 0.542,
        "market_probability": 0.525,
        "edge": 0.017,
        "confidence_band": (0.518, 0.566)
    }
}
```

## Configuration

### Agent Configuration

Control which agents are active:

```python
# config.py
ENABLE_ADVANCED_AGENTS = True  # Enable all 13 agents
# Set to False to use only MVP agents (faster, cheaper)
```

### LLM Configuration

Configure the Gradient AI model:

```python
LLM_MODEL = "meta-llama/llama-3.1-70b-instruct"  # High quality
# Or use smaller models for faster/cheaper analysis:
# LLM_MODEL = "meta-llama/llama-3.1-8b-instruct"
```

### Timeout Configuration

Adjust agent execution timeouts:

```python
AGENT_TIMEOUT_MS = 30000  # 30 seconds per agent
MAX_RETRIES = 3  # Retry failed agents up to 3 times
```

## Customization

### Adding Custom Agents

1. Create a new agent module in `agents/`:

```python
# agents/my_custom_agent.py
AGENT_NAME = "my_custom_agent"

SYSTEM_PROMPT = """You are a specialized market analyst focusing on [your domain].

Analyze the market and provide:
1. Your assessment of the outcome probability
2. Key factors driving your analysis
3. Risks and uncertainties

Market Data:
{mbd}

Memory Context:
{memory_context}

Provide your analysis as a structured AgentSignal."""
```

2. Register the agent in `main.py`:

```python
from agents.my_custom_agent import AGENT_NAME, SYSTEM_PROMPT

# Add to agent creation
my_custom_agent_node = create_agent_node(AGENT_NAME, SYSTEM_PROMPT, config)
workflow.add_node(AGENT_NAME, my_custom_agent_node)
```

### Customizing Prompts

All prompts are centralized in `prompts.py`. Edit them to change agent behavior:

```python
# prompts.py
MARKET_MICROSTRUCTURE_PROMPT = """You are a market microstructure analyst...

[Customize the prompt here]
"""
```

### Adjusting Consensus Logic

Modify the consensus engine in `nodes/consensus_engine.py`:

```python
# Change weighting strategy
def calculate_weighted_consensus(signals):
    # Custom weighting logic
    weights = [signal.confidence ** 2 for signal in signals]  # Square confidence
    # ... rest of calculation
```

## Testing

### Run All Tests

```bash
pytest
```

### Run Unit Tests Only

```bash
pytest -m "not property"
```

### Run Property-Based Tests

```bash
pytest -m property
```

### Run Specific Test File

```bash
pytest agents/test_agent_factory.py
```

### Run with Coverage

```bash
pytest --cov=. --cov-report=html
```

## Observability

### Opik Integration

TradeWizard DOA integrates with Opik for comprehensive LLM observability:

- **Trace all LLM calls**: Every agent execution is traced
- **Cost tracking**: Token usage and estimated costs per analysis
- **Performance monitoring**: Latency and success rates
- **Error tracking**: Failed calls and retry attempts

View traces in the Opik dashboard at https://www.comet.com/opik

### Audit Logging

All workflow stages are logged with structured audit entries:

```python
{
    "timestamp": 1704067200,
    "stage": "agent_execution",
    "agent_name": "market_microstructure",
    "status": "success",
    "duration_ms": 2340,
    "metadata": {}
}
```

Access audit logs in the database `analysis_history` table.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Invalid condition_id" | Verify the condition ID exists on Polymarket |
| "Gradient AI authentication failed" | Check `GRADIENT_ACCESS_TOKEN` and `GRADIENT_WORKSPACE_ID` |
| "Database connection error" | Verify Supabase credentials and network connectivity |
| "Agent timeout" | Increase `AGENT_TIMEOUT_MS` or use a faster LLM model |
| "Insufficient agent signals" | Ensure at least 2 agents complete successfully |
| "No trading edge detected" | Market is fairly priced; no recommendation generated |

## Performance Optimization

### Reduce Analysis Time

1. **Use smaller LLM models**: Switch to `llama-3.1-8b-instruct`
2. **Disable advanced agents**: Set `ENABLE_ADVANCED_AGENTS=false`
3. **Reduce agent timeout**: Lower `AGENT_TIMEOUT_MS` to 15000
4. **Limit memory retrieval**: Reduce historical context window

### Reduce Costs

1. **Use MVP agents only**: Disable advanced agents
2. **Batch analyses**: Analyze multiple markets in sequence to reuse connections
3. **Cache market data**: Implement caching for frequently accessed markets
4. **Use smaller models**: Trade accuracy for cost with smaller LLMs

## Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Gradient AI Platform](https://docs.digitalocean.com/products/gradient/)
- [Polymarket API Documentation](https://docs.polymarket.com/)
- [Opik Observability](https://www.comet.com/docs/opik/)
- [Supabase Documentation](https://supabase.com/docs)

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please open an issue or pull request for:
- New agent implementations
- Performance improvements
- Bug fixes
- Documentation enhancements
