"""
Probability Baseline Agent

This agent establishes a rational baseline probability estimate using fundamental analysis,
base rates, and statistical reasoning before considering market dynamics or sentiment.

The agent focuses on:
- Base rate analysis from historical precedents
- Fundamental probability drivers
- Statistical models and forecasting methods
- Reference class forecasting
- Conditional probability analysis
"""

from prompts import PROBABILITY_BASELINE_PROMPT

# Agent identifier used in the workflow
AGENT_NAME = "probability_baseline"

# System prompt defining the agent's analysis perspective
SYSTEM_PROMPT = PROBABILITY_BASELINE_PROMPT
