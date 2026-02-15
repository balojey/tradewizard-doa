"""
Market Microstructure Agent

This agent analyzes order book dynamics, liquidity conditions, and trading patterns
to assess market efficiency and identify potential trading opportunities in prediction markets.

The agent focuses on:
- Order book depth and liquidity distribution
- Bid-ask spread and transaction costs
- Volume patterns and trading velocity
- Market maker behavior and liquidity provision
- Price discovery efficiency
"""

from prompts import MARKET_MICROSTRUCTURE_PROMPT

# Agent identifier used in the workflow
AGENT_NAME = "market_microstructure"

# System prompt defining the agent's analysis perspective
SYSTEM_PROMPT = MARKET_MICROSTRUCTURE_PROMPT
