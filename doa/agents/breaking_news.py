"""
Breaking News Agent

This agent identifies and assesses breaking news developments that could materially
impact prediction market outcomes, focusing on information velocity, source credibility,
and market-moving potential.

The agent focuses on:
- Breaking news developments and real-time updates
- Information velocity and propagation speed
- Source credibility and verification status
- Market-moving potential of new information
- News sentiment and directional implications
- Information gaps and unconfirmed reports
- Time-sensitive catalysts and deadlines
"""

from prompts import BREAKING_NEWS_PROMPT

# Agent identifier used in the workflow
AGENT_NAME = "breaking_news"

# System prompt defining the agent's analysis perspective
SYSTEM_PROMPT = BREAKING_NEWS_PROMPT
