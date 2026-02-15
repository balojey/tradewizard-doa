"""
Polling Intelligence Agent

This agent analyzes prediction markets as aggregated polling mechanisms, assessing
market participant beliefs, information aggregation efficiency, and crowd intelligence signals.

The agent focuses on:
- Market as polling mechanism: Interpreting prices as aggregated beliefs
- Participant diversity and information distribution
- Crowd wisdom vs. crowd madness indicators
- Information aggregation efficiency
- Belief updating patterns and market learning
- Participant sophistication and expertise signals
- Consensus formation and belief convergence
- Contrarian signals and minority views
"""

from prompts import POLLING_INTELLIGENCE_PROMPT

# Agent identifier used in the workflow
AGENT_NAME = "polling_intelligence"

# System prompt defining the agent's analysis perspective
SYSTEM_PROMPT = POLLING_INTELLIGENCE_PROMPT
