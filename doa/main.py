"""
TradeWizard DOA - Market Analysis Workflow

This module implements the main LangGraph workflow for analyzing prediction markets
on Polymarket using specialized AI agents. The workflow orchestrates:

1. Market data ingestion from Polymarket
2. Historical memory retrieval for agent context
3. Keyword extraction for dynamic agent selection
4. Parallel execution of specialized intelligence agents
5. Signal fusion and thesis construction
6. Cross-examination and consensus building
7. Trade recommendation generation

Based on TradeWizard's multi-agent architecture, ported to Python and Digital Ocean's
Gradient AI Platform.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from langgraph.checkpoint.memory import MemorySaver

# Optional PostgreSQL checkpointer
try:
    from langgraph.checkpoint.postgres import PostgresSaver
except ImportError:
    PostgresSaver = None

from config import EngineConfig, load_config
from models.state import GraphState
from models.types import AnalysisResult, AuditEntry
from tools.polymarket_client import PolymarketClient
from database.supabase_client import SupabaseClient
from database.persistence import PersistenceLayer

# Import node factories
from nodes.market_ingestion import create_market_ingestion_node
from nodes.memory_retrieval import create_memory_retrieval_node
from nodes.keyword_extraction import create_keyword_extraction_node
from nodes.dynamic_agent_selection import create_dynamic_agent_selection_node
from nodes.agent_signal_fusion import create_agent_signal_fusion_node
from nodes.thesis_construction import create_thesis_construction_node
from nodes.cross_examination import create_cross_examination_node
from nodes.consensus_engine import create_consensus_engine_node
from nodes.recommendation_generation import create_recommendation_generation_node

# Import agent factory and agent modules
from agents.agent_factory import create_agent_node
from agents import (
    market_microstructure,
    probability_baseline,
    risk_assessment,
    breaking_news,
    event_impact,
    polling_intelligence,
    historical_pattern,
    media_sentiment,
    social_sentiment,
    narrative_velocity,
    momentum,
    mean_reversion,
    catalyst,
    tail_risk,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TradeWizard")


# ============================================================================
# AGENT NODE CREATION
# ============================================================================

def create_all_agent_nodes(config: EngineConfig) -> Dict[str, Any]:
    """
    Create all agent nodes using the agent factory.
    
    This function creates agent nodes for all available intelligence agents,
    each with their specific system prompt and configuration.
    
    Args:
        config: Engine configuration
        
    Returns:
        Dictionary mapping agent names to their node functions
    """
    agent_nodes = {}
    
    # MVP Agents
    if config.agents.enable_mvp_agents:
        agent_nodes['market_microstructure'] = create_agent_node(
            agent_name=market_microstructure.AGENT_NAME,
            system_prompt=market_microstructure.SYSTEM_PROMPT,
            config=config
        )
        agent_nodes['probability_baseline'] = create_agent_node(
            agent_name=probability_baseline.AGENT_NAME,
            system_prompt=probability_baseline.SYSTEM_PROMPT,
            config=config
        )
        agent_nodes['risk_assessment'] = create_agent_node(
            agent_name=risk_assessment.AGENT_NAME,
            system_prompt=risk_assessment.SYSTEM_PROMPT,
            config=config
        )
    
    # Event Intelligence Agents
    if config.agents.enable_event_intelligence:
        # Use autonomous breaking news agent
        agent_nodes['breaking_news'] = breaking_news.create_breaking_news_agent_node(config)
        agent_nodes['event_impact'] = create_agent_node(
            agent_name=event_impact.AGENT_NAME,
            system_prompt=event_impact.SYSTEM_PROMPT,
            config=config
        )
    
    # Polling & Statistical Agents
    if config.agents.enable_polling_statistical:
        # Use autonomous polling intelligence agent
        agent_nodes['polling_intelligence'] = polling_intelligence.create_polling_intelligence_agent_node(config)
        agent_nodes['historical_pattern'] = create_agent_node(
            agent_name=historical_pattern.AGENT_NAME,
            system_prompt=historical_pattern.SYSTEM_PROMPT,
            config=config
        )
    
    # Sentiment & Narrative Agents
    if config.agents.enable_sentiment_narrative:
        # Use autonomous media sentiment agent
        agent_nodes['media_sentiment'] = media_sentiment.create_media_sentiment_agent_node(config)
        agent_nodes['social_sentiment'] = create_agent_node(
            agent_name=social_sentiment.AGENT_NAME,
            system_prompt=social_sentiment.SYSTEM_PROMPT,
            config=config
        )
        agent_nodes['narrative_velocity'] = create_agent_node(
            agent_name=narrative_velocity.AGENT_NAME,
            system_prompt=narrative_velocity.SYSTEM_PROMPT,
            config=config
        )
    
    # Price Action Agents
    if config.agents.enable_price_action:
        agent_nodes['momentum'] = create_agent_node(
            agent_name=momentum.AGENT_NAME,
            system_prompt=momentum.SYSTEM_PROMPT,
            config=config
        )
        agent_nodes['mean_reversion'] = create_agent_node(
            agent_name=mean_reversion.AGENT_NAME,
            system_prompt=mean_reversion.SYSTEM_PROMPT,
            config=config
        )
    
    # Event Scenario Agents
    if config.agents.enable_event_scenario:
        agent_nodes['catalyst'] = create_agent_node(
            agent_name=catalyst.AGENT_NAME,
            system_prompt=catalyst.SYSTEM_PROMPT,
            config=config
        )
        agent_nodes['tail_risk'] = create_agent_node(
            agent_name=tail_risk.AGENT_NAME,
            system_prompt=tail_risk.SYSTEM_PROMPT,
            config=config
        )
    
    logger.info(f"Created {len(agent_nodes)} agent nodes")
    return agent_nodes


# ============================================================================
# PARALLEL AGENT DISPATCH
# ============================================================================

def dispatch_parallel_agents(state: GraphState) -> List[Send]:
    """
    Fan-out: Dispatch parallel execution for all active agents using Send API.
    
    This function creates a Send command for each active agent, which will be
    executed in parallel by LangGraph. Results are automatically collected via
    the Annotated reducer in GraphState.
    
    Args:
        state: Current workflow state with active_agents list
        
    Returns:
        List of Send commands for parallel agent execution
    """
    active_agents = state.get("active_agents", [])
    
    if not active_agents:
        logger.warning("No active agents to dispatch")
        return []
    
    logger.info(f"Dispatching {len(active_agents)} agents for parallel execution")
    
    sends = []
    for agent_name in active_agents:
        logger.info(f"  -> Dispatching agent: {agent_name}")
        sends.append(Send(agent_name, state))
    
    return sends



# ============================================================================
# WORKFLOW GRAPH CONSTRUCTION
# ============================================================================

def build_market_analysis_graph(config: EngineConfig) -> StateGraph:
    """
    Build the LangGraph workflow for market analysis.
    
    This function constructs the complete workflow graph with all nodes and edges:
    
    Workflow Structure:
    1. START → market_ingestion
    2. market_ingestion → memory_retrieval
    3. memory_retrieval → keyword_extraction
    4. keyword_extraction → dynamic_agent_selection
    5. dynamic_agent_selection → [parallel agents] (via Send API)
    6. [all agents] → agent_signal_fusion (fan-in)
    7. agent_signal_fusion → thesis_construction
    8. thesis_construction → cross_examination
    9. cross_examination → consensus_engine
    10. consensus_engine → recommendation_generation
    11. recommendation_generation → END
    
    Args:
        config: Engine configuration
        
    Returns:
        Compiled StateGraph ready for execution
    """
    logger.info("Building market analysis workflow graph")
    
    # Initialize dependencies
    polymarket_client = PolymarketClient(config.polymarket)
    
    # Initialize database persistence (optional)
    persistence_layer = None
    if config.database.enable_persistence:
        try:
            supabase_client = SupabaseClient(config.database)
            persistence_layer = PersistenceLayer(supabase_client)
            logger.info("Database persistence enabled")
        except Exception as e:
            logger.warning(f"Failed to initialize database persistence: {e}")
            logger.warning("Continuing without persistence")
    
    # Create workflow graph
    workflow = StateGraph(GraphState)
    
    # ========================================================================
    # Add workflow nodes
    # ========================================================================
    
    # Market ingestion node
    workflow.add_node(
        "market_ingestion",
        create_market_ingestion_node(polymarket_client, config)
    )
    
    # Memory retrieval node
    workflow.add_node(
        "memory_retrieval",
        create_memory_retrieval_node(persistence_layer, config)
    )
    
    # Keyword extraction node
    workflow.add_node(
        "keyword_extraction",
        create_keyword_extraction_node(config)
    )
    
    # Dynamic agent selection node
    workflow.add_node(
        "dynamic_agent_selection",
        create_dynamic_agent_selection_node(config)
    )
    
    # Add all agent nodes
    agent_nodes = create_all_agent_nodes(config)
    for agent_name, agent_node in agent_nodes.items():
        workflow.add_node(agent_name, agent_node)
    
    # Agent signal fusion node (fan-in point)
    workflow.add_node(
        "agent_signal_fusion",
        create_agent_signal_fusion_node(config)
    )
    
    # Thesis construction node
    workflow.add_node(
        "thesis_construction",
        create_thesis_construction_node(config)
    )
    
    # Cross-examination node
    workflow.add_node(
        "cross_examination",
        create_cross_examination_node(config)
    )
    
    # Consensus engine node
    workflow.add_node(
        "consensus_engine",
        create_consensus_engine_node(config)
    )
    
    # Recommendation generation node
    workflow.add_node(
        "recommendation_generation",
        create_recommendation_generation_node(config, persistence_layer)
    )
    
    # ========================================================================
    # Define workflow edges
    # ========================================================================
    
    # Sequential edges: START → market_ingestion → memory_retrieval → keyword_extraction → dynamic_agent_selection
    workflow.add_edge(START, "market_ingestion")
    workflow.add_edge("market_ingestion", "memory_retrieval")
    workflow.add_edge("memory_retrieval", "keyword_extraction")
    workflow.add_edge("keyword_extraction", "dynamic_agent_selection")
    
    # Conditional edges for parallel agent dispatch (fan-out)
    # dispatch_parallel_agents returns List[Send] for each active agent
    workflow.add_conditional_edges(
        "dynamic_agent_selection",
        dispatch_parallel_agents,
        list(agent_nodes.keys())  # All possible agent destinations
    )
    
    # All agent nodes converge to signal fusion (fan-in)
    for agent_name in agent_nodes.keys():
        workflow.add_edge(agent_name, "agent_signal_fusion")
    
    # Sequential edges: signal_fusion → thesis_construction → cross_examination → consensus_engine → recommendation_generation → END
    workflow.add_edge("agent_signal_fusion", "thesis_construction")
    workflow.add_edge("thesis_construction", "cross_examination")
    workflow.add_edge("cross_examination", "consensus_engine")
    workflow.add_edge("consensus_engine", "recommendation_generation")
    workflow.add_edge("recommendation_generation", END)
    
    logger.info("Workflow graph construction complete")
    
    return workflow



def create_checkpointer(config: EngineConfig):
    """
    Create appropriate checkpointer based on configuration.
    
    Supports:
    - memory: In-memory checkpointer (MemorySaver)
    - sqlite: SQLite-based checkpointer
    - postgres: PostgreSQL-based checkpointer
    
    Args:
        config: Engine configuration
        
    Returns:
        Checkpointer instance or None
    """
    checkpointer_type = config.langgraph.checkpointer_type.lower()
    
    if checkpointer_type == "memory":
        logger.info("Using in-memory checkpointer")
        return MemorySaver()
    
    elif checkpointer_type == "sqlite":
        logger.info(f"Using SQLite checkpointer: {config.langgraph.sqlite_path}")
        try:
            from langgraph.checkpoint.sqlite import SqliteSaver
            return SqliteSaver.from_conn_string(config.langgraph.sqlite_path)
        except ImportError:
            logger.warning("SQLite checkpointer not available, falling back to memory")
            return MemorySaver()
    
    elif checkpointer_type == "postgres":
        logger.info("Using PostgreSQL checkpointer")
        if PostgresSaver is None:
            logger.warning("PostgreSQL checkpointer not available, falling back to memory")
            return MemorySaver()
        try:
            if config.database.postgres_connection_string:
                return PostgresSaver.from_conn_string(
                    config.database.postgres_connection_string
                )
            else:
                logger.warning("No PostgreSQL connection string, falling back to memory")
                return MemorySaver()
        except Exception as e:
            logger.warning(f"Failed to create PostgreSQL checkpointer: {e}")
            return MemorySaver()
    
    else:
        logger.warning(f"Unknown checkpointer type: {checkpointer_type}, using memory")
        return MemorySaver()


# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================

async def analyze_market(
    condition_id: str,
    config: Optional[EngineConfig] = None
) -> AnalysisResult:
    """
    Analyze a prediction market and generate trade recommendation.
    
    This is the main entry point for market analysis. It:
    1. Builds the workflow graph
    2. Invokes the graph with the condition_id
    3. Returns the complete analysis result
    
    Args:
        condition_id: Polymarket condition ID to analyze
        config: Engine configuration (loads from env if not provided)
        
    Returns:
        AnalysisResult with recommendation, agent signals, and audit log
        
    Raises:
        ValueError: If condition_id is invalid
        Exception: If workflow execution fails
        
    Examples:
        >>> config = load_config()
        >>> result = await analyze_market("0xabc123", config)
        >>> print(result.recommendation.action)
        'LONG_YES'
    """
    start_time = time.time()
    
    # Validate input
    if not condition_id:
        raise ValueError("condition_id is required")
    
    # Load config if not provided
    if config is None:
        config = load_config()
    
    logger.info("=" * 80)
    logger.info("TRADEWIZARD MARKET ANALYSIS")
    logger.info("=" * 80)
    logger.info(f"Condition ID: {condition_id}")
    logger.info(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Build workflow graph
        workflow = build_market_analysis_graph(config)
        
        # Create checkpointer
        checkpointer = create_checkpointer(config)
        
        # Compile graph with checkpointer
        graph = workflow.compile(checkpointer=checkpointer)
        
        logger.info("Workflow graph compiled successfully")
        
        # Initialize state
        initial_state: GraphState = {
            "condition_id": condition_id,
            "agent_signals": [],
            "agent_errors": [],
            "audit_log": [],
            "memory_context": {}
        }
        
        # Invoke graph
        logger.info("Starting workflow execution...")
        
        final_state = await graph.ainvoke(initial_state)
        
        duration_s = time.time() - start_time
        
        logger.info("=" * 80)
        logger.info("WORKFLOW EXECUTION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Duration: {duration_s:.2f}s")
        logger.info(f"Agent signals: {len(final_state.get('agent_signals', []))}")
        logger.info(f"Agent errors: {len(final_state.get('agent_errors', []))}")
        
        # Extract results from final state
        recommendation = final_state.get("recommendation")
        agent_signals = final_state.get("agent_signals", [])
        agent_errors = final_state.get("agent_errors", [])
        consensus = final_state.get("consensus")
        debate_record = final_state.get("debate_record")
        audit_log = final_state.get("audit_log", [])
        
        # Log recommendation
        if recommendation:
            logger.info(f"Recommendation: {recommendation.action}")
            logger.info(f"  Entry Zone: {recommendation.entry_zone}")
            logger.info(f"  Expected Value: ${recommendation.expected_value:.2f}")
            logger.info(f"  Win Probability: {recommendation.win_probability:.1%}")
        else:
            logger.warning("No recommendation generated")
        
        # Create analysis result
        result = AnalysisResult(
            recommendation=recommendation,
            agent_signals=agent_signals,
            agent_errors=agent_errors,
            consensus=consensus,
            debate_record=debate_record,
            audit_log=audit_log,
            analysis_timestamp=int(time.time())
        )
        
        logger.info("Analysis complete")
        
        return result
    
    except Exception as e:
        duration_s = time.time() - start_time
        logger.error(f"Market analysis failed after {duration_s:.2f}s: {e}", exc_info=True)
        raise



# ============================================================================
# CLI ENTRY POINT (for testing)
# ============================================================================

async def main():
    """
    CLI entry point for testing market analysis.
    
    Usage:
        python main.py [condition_id]
    """
    import sys
    
    # Get condition_id from command line or use default
    if len(sys.argv) > 1:
        condition_id = sys.argv[1]
    else:
        # Default test condition ID
        condition_id = "0x0e7c1d14b2f1cc1b0e0f8e5e5e5e5e5e5e5e5e5e"
        logger.info(f"No condition_id provided, using test ID: {condition_id}")
    
    try:
        # Load configuration
        config = load_config()
        
        # Run analysis
        result = await analyze_market(condition_id, config)
        
        # Print results
        print("\n" + "=" * 80)
        print("ANALYSIS RESULTS")
        print("=" * 80)
        
        if result.recommendation:
            print(f"\nAction: {result.recommendation.action}")
            print(f"Entry Zone: {result.recommendation.entry_zone}")
            print(f"Target Zone: {result.recommendation.target_zone}")
            print(f"Expected Value: ${result.recommendation.expected_value:.2f}")
            print(f"Win Probability: {result.recommendation.win_probability:.1%}")
            print(f"Liquidity Risk: {result.recommendation.liquidity_risk}")
            print(f"\nExplanation:")
            print(f"  {result.recommendation.explanation.summary}")
        else:
            print("\nNo recommendation generated")
        
        print(f"\nAgent Signals: {len(result.agent_signals)}")
        for signal in result.agent_signals:
            print(f"  - {signal.agent_name}: {signal.direction} "
                  f"(prob={signal.fair_probability:.2%}, conf={signal.confidence:.2%})")
        
        if result.agent_errors:
            print(f"\nAgent Errors: {len(result.agent_errors)}")
            for error in result.agent_errors:
                print(f"  - {error.agent_name}: {error.type} - {error.message}")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
