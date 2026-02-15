"""
Media Sentiment Agent

This agent assesses media sentiment, narrative framing, and editorial positioning
to understand how media coverage influences public perception and market outcomes.

The agent focuses on:
- Media sentiment analysis (positive, negative, neutral)
- Narrative framing and editorial positioning
- Media coverage volume and prominence
- Source diversity and ideological balance
- Sentiment shifts and trend analysis
- Media influence on public opinion
- Credibility and bias assessment
- Coverage gaps and underreported angles
"""

from prompts import MEDIA_SENTIMENT_PROMPT

# Agent identifier used in the workflow
AGENT_NAME = "media_sentiment"

# System prompt defining the agent's analysis perspective
SYSTEM_PROMPT = MEDIA_SENTIMENT_PROMPT
