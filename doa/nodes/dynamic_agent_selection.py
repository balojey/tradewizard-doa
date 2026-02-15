"""Dynamic agent selection node for LangGraph workflow."""

import logging
import time
from typing import Any, Dict, List, Set

from models.state import GraphState, EventKeywords
from models.types import AuditEntry, MarketBriefingDocument
from config import EngineConfig, AgentConfig

logger = logging.getLogger(__name__)


def select_agents_by_keywords(
    keywords: EventKeywords,
    event_type: str,
    config: AgentConfig
) -> Set[str]:
    """
    Select specialized agents based on keywords and event type.
    
    This function determines which advanced agents should be activated
    based on the presence of relevant keywords in the market data.
    
    Agent Selection Rules:
    - Event Intelligence: Activated for breaking news keywords
    - Polling & Statistical: Activated for election/polling keywords
    - Sentiment & Narrative: Activated for social/media keywords
    - Price Action: Always activated if enabled
    - Event Scenario: Activated for catalyst/risk keywords
    
    Args:
        keywords: Event and market level keywords
        event_type: Type of event (election, policy, etc.)
        config: Agent configuration
        
    Returns:
        Set of agent names to activate
    """
    selected_agents: Set[str] = set()
    
    # Combine all keywords for matching
    all_keywords = keywords.get("event_level", []) + keywords.get("market_level", [])
    all_keywords_lower = [k.lower() for k in all_keywords]
    
    # Event Intelligence agents - activated for news/breaking events
    if config.enable_event_intelligence:
        news_keywords = {'breaking', 'news', 'announcement', 'report', 'statement', 'press'}
        if any(kw in ' '.join(all_keywords_lower) for kw in news_keywords):
            selected_agents.add('breaking_news')
            selected_agents.add('event_impact')
    
    # Polling & Statistical agents - activated for elections/polls
    if config.enable_polling_statistical:
        polling_keywords = {'poll', 'polling', 'election', 'vote', 'voter', 'survey', 'approval'}
        if (event_type == 'election' or 
            any(kw in ' '.join(all_keywords_lower) for kw in polling_keywords)):
            selected_agents.add('polling_intelligence')
            selected_agents.add('historical_pattern')
    
    # Sentiment & Narrative agents - activated for social/media topics
    if config.enable_sentiment_narrative:
        sentiment_keywords = {'social', 'media', 'twitter', 'sentiment', 'narrative', 'public'}
        if any(kw in ' '.join(all_keywords_lower) for kw in sentiment_keywords):
            selected_agents.add('media_sentiment')
            selected_agents.add('social_sentiment')
            selected_agents.add('narrative_velocity')
    
    # Price Action agents - always activated if enabled (analyze market dynamics)
    if config.enable_price_action:
        selected_agents.add('momentum')
        selected_agents.add('mean_reversion')
    
    # Event Scenario agents - activated for catalyst/risk keywords
    if config.enable_event_scenario:
        scenario_keywords = {'catalyst', 'risk', 'scenario', 'outcome', 'impact', 'consequence'}
        if any(kw in ' '.join(all_keywords_lower) for kw in scenario_keywords):
            selected_agents.add('catalyst')
            selected_agents.add('tail_risk')
    
    return selected_agents


async def dynamic_agent_selection_node(
    state: GraphState,
    config: EngineConfig
) -> Dict[str, Any]:
    """
    Determine which agents should be activated for analysis.
    
    This node implements dynamic agent selection based on:
    1. Market keywords (from keyword extraction)
    2. Event type (election, policy, etc.)
    3. Agent configuration (which categories are enabled)
    
    Selection Strategy:
    - MVP agents (market_microstructure, probability_baseline, risk_assessment)
      are ALWAYS included if enabled
    - Advanced agents are conditionally included based on keyword matching
    - This allows the system to scale resources based on market characteristics
    
    Args:
        state: Current workflow state with mbd and market_keywords
        config: Engine configuration with agent settings
        
    Returns:
        State update with active_agents list and audit entry
        
    State Requirements:
        - mbd: Market Briefing Document (required)
        - market_keywords: EventKeywords (optional, will use empty if missing)
        
    State Updates:
        - active_agents: List of agent names to activate
        - audit_log: Audit entry for agent selection stage
        
    Examples:
        >>> state = {
        ...     "mbd": MarketBriefingDocument(...),
        ...     "market_keywords": {"event_level": ["Election"], "market_level": ["Poll"]}
        ... }
        >>> result = await dynamic_agent_selection_node(state, config)
        >>> print(result["active_agents"])
        ['market_microstructure', 'probability_baseline', 'risk_assessment', 
         'polling_intelligence', 'historical_pattern']
    """
    start_time = time.time()
    
    # Extract required state
    mbd = state.get("mbd")
    market_keywords = state.get("market_keywords", EventKeywords(event_level=[], market_level=[]))
    
    # Validate required state
    if not mbd:
        logger.error("Dynamic agent selection node called without MBD")
        return {
            "active_agents": [],
            "audit_log": [AuditEntry(
                stage="dynamic_agent_selection",
                timestamp=int(time.time()),
                status="failed",
                details={"error": "Missing market briefing document"}
            )]
        }
    
    logger.info(f"Selecting agents for market: {mbd.question}")
    
    try:
        active_agents: List[str] = []
        
        # Always include MVP agents if enabled
        if config.agents.enable_mvp_agents:
            mvp_agents = [
                'market_microstructure',
                'probability_baseline',
                'risk_assessment'
            ]
            active_agents.extend(mvp_agents)
            logger.info(f"Added {len(mvp_agents)} MVP agents")
        
        # Select advanced agents based on keywords and event type
        advanced_agents = select_agents_by_keywords(
            keywords=market_keywords,
            event_type=mbd.event_type,
            config=config.agents
        )
        
        if advanced_agents:
            active_agents.extend(sorted(advanced_agents))
            logger.info(f"Added {len(advanced_agents)} advanced agents: {sorted(advanced_agents)}")
        
        # Ensure we have at least minimum required agents
        if len(active_agents) < config.consensus.min_agents_required:
            logger.warning(
                f"Only {len(active_agents)} agents selected, "
                f"but minimum required is {config.consensus.min_agents_required}"
            )
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        logger.info(
            f"Agent selection completed in {duration_ms}ms: "
            f"{len(active_agents)} agents selected"
        )
        
        return {
            "active_agents": active_agents,
            "audit_log": [AuditEntry(
                stage="dynamic_agent_selection",
                timestamp=int(time.time()),
                status="completed",
                details={
                    "duration_ms": duration_ms,
                    "total_agents": len(active_agents),
                    "mvp_agents": 3 if config.agents.enable_mvp_agents else 0,
                    "advanced_agents": len(advanced_agents),
                    "selected_agents": active_agents,
                    "event_type": mbd.event_type,
                    "keyword_count": len(market_keywords.get("event_level", [])) + 
                                   len(market_keywords.get("market_level", []))
                }
            )]
        }
    
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Agent selection failed after {duration_ms}ms: {e}")
        
        # Fallback to MVP agents only
        fallback_agents = []
        if config.agents.enable_mvp_agents:
            fallback_agents = [
                'market_microstructure',
                'probability_baseline',
                'risk_assessment'
            ]
        
        return {
            "active_agents": fallback_agents,
            "audit_log": [AuditEntry(
                stage="dynamic_agent_selection",
                timestamp=int(time.time()),
                status="failed",
                details={
                    "duration_ms": duration_ms,
                    "error": str(e),
                    "fallback": "mvp_agents_only",
                    "fallback_count": len(fallback_agents)
                }
            )]
        }


def create_dynamic_agent_selection_node(config: EngineConfig):
    """
    Factory function to create dynamic agent selection node with dependencies.
    
    This factory pattern allows the node to be created with the required
    dependencies (config) while maintaining the standard LangGraph node signature.
    
    Args:
        config: Engine configuration
        
    Returns:
        Async function that takes state and returns state update
        
    Examples:
        >>> config = load_config()
        >>> node = create_dynamic_agent_selection_node(config)
        >>> result = await node(state)
    """
    async def node(state: GraphState) -> Dict[str, Any]:
        return await dynamic_agent_selection_node(state, config)
    
    return node
