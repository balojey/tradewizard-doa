# Product Overview

TradeWizard is an AI-powered prediction trading platform that provides intelligent analysis and trading recommendations for real-world outcomes on Polymarket.

## Core Value Proposition

Transforms prediction markets from speculative guessing into guided, intelligence-driven trading through multi-agent AI analysis.

## Key Components

- **tradewizard-agents**: Multi-agent backend system (Node.js + LangGraph) that orchestrates specialized AI agents for market analysis
- **tradewizard-frontend**: Web application (Next.js + React) providing user interface for market discovery and trading
- **doa**: Python-based replication of the multi-agent system using Digital Ocean's Gradient AI Platform

## Multi-Agent Intelligence System

The platform uses specialized AI agents that analyze markets from multiple perspectives:

- Market microstructure and liquidity analysis
- Probability baseline estimation
- Risk assessment and tail risk modeling
- Breaking news and event impact analysis
- Polling intelligence and historical patterns
- Media and social sentiment tracking
- Price momentum and mean reversion signals
- Catalyst identification and narrative velocity

## Workflow

1. **Market Ingestion**: Fetch market data from Polymarket APIs
2. **Memory Retrieval**: Load historical agent signals for context
3. **Parallel Agent Execution**: All agents analyze simultaneously
4. **Thesis Construction**: Build bull and bear theses
5. **Cross-Examination**: Adversarial testing of assumptions
6. **Consensus Engine**: Calculate unified probability estimate
7. **Recommendation Generation**: Create actionable trade signals with entry/exit zones and risk assessment

## Key Features

- Explainable AI recommendations with clear reasoning
- Adversarial debate protocol to prevent groupthink
- Real-time data integration (Polymarket, NewsData.io)
- Full observability with Opik integration
- Agent memory system for closed-loop analysis
- Autonomous tool-calling agents that fetch data dynamically
