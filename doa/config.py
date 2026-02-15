"""Configuration management for TradeWizard DOA replication."""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class PolymarketConfig:
    """Polymarket API configuration."""
    gamma_api_url: str
    clob_api_url: str
    api_key: Optional[str] = None


@dataclass
class LLMConfig:
    """Gradient AI LLM configuration."""
    model_name: str
    temperature: float
    max_tokens: int
    timeout_ms: int


@dataclass
class AgentConfig:
    """Agent execution configuration."""
    timeout_ms: int
    max_retries: int
    enable_mvp_agents: bool
    enable_event_intelligence: bool
    enable_polling_statistical: bool
    enable_sentiment_narrative: bool
    enable_price_action: bool
    enable_event_scenario: bool


@dataclass
class DatabaseConfig:
    """Supabase/PostgreSQL configuration."""
    supabase_url: Optional[str]
    supabase_key: Optional[str]
    postgres_connection_string: Optional[str]
    enable_persistence: bool


@dataclass
class OpikConfig:
    """Opik observability configuration."""
    api_key: Optional[str]
    workspace: Optional[str]
    project_name: str
    enable_tracing: bool


@dataclass
class ConsensusConfig:
    """Consensus engine configuration."""
    min_agents_required: int
    disagreement_threshold: float
    confidence_band_multiplier: float
    min_edge_threshold: float


@dataclass
class MemorySystemConfig:
    """Memory retrieval configuration."""
    enable_memory: bool
    max_historical_signals: int
    memory_timeout_ms: int


@dataclass
class LangGraphConfig:
    """LangGraph workflow configuration."""
    checkpointer_type: str  # "memory", "sqlite", "postgres"
    sqlite_path: Optional[str]


@dataclass
class EngineConfig:
    """Main engine configuration."""
    polymarket: PolymarketConfig
    langgraph: LangGraphConfig
    opik: OpikConfig
    llm: LLMConfig
    agents: AgentConfig
    consensus: ConsensusConfig
    database: DatabaseConfig
    memory_system: MemorySystemConfig


def load_config() -> EngineConfig:
    """
    Load configuration from environment variables.
    
    Returns:
        EngineConfig with all settings loaded from environment
        
    Raises:
        ValueError: If required configuration is missing
    """
    # Validate required fields
    required_vars = {
        "DIGITALOCEAN_INFERENCE_KEY": os.getenv("DIGITALOCEAN_INFERENCE_KEY"),
        "POLYMARKET_GAMMA_API_URL": os.getenv("POLYMARKET_GAMMA_API_URL", "https://gamma-api.polymarket.com"),
        "POLYMARKET_CLOB_API_URL": os.getenv("POLYMARKET_CLOB_API_URL", "https://clob.polymarket.com"),
    }
    
    missing = [key for key, value in required_vars.items() if not value]
    if missing:
        raise ValueError(f"Missing required configuration: {', '.join(missing)}")
    
    # Polymarket configuration
    polymarket = PolymarketConfig(
        gamma_api_url=os.getenv("POLYMARKET_GAMMA_API_URL", "https://gamma-api.polymarket.com"),
        clob_api_url=os.getenv("POLYMARKET_CLOB_API_URL", "https://clob.polymarket.com"),
        api_key=os.getenv("POLYMARKET_API_KEY")
    )
    
    # LangGraph configuration
    langgraph = LangGraphConfig(
        checkpointer_type=os.getenv("LANGGRAPH_CHECKPOINTER", "memory"),
        sqlite_path=os.getenv("LANGGRAPH_SQLITE_PATH", "./checkpoints.db")
    )
    
    # Opik configuration
    opik = OpikConfig(
        api_key=os.getenv("OPIK_API_KEY"),
        workspace=os.getenv("OPIK_WORKSPACE"),
        project_name=os.getenv("OPIK_PROJECT_NAME", "tradewizard-doa"),
        enable_tracing=os.getenv("OPIK_ENABLE_TRACING", "true").lower() == "true"
    )
    
    # LLM configuration
    llm = LLMConfig(
        model_name=os.getenv("LLM_MODEL_NAME", "llama-3.3-70b-instruct"),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2000")),
        timeout_ms=int(os.getenv("LLM_TIMEOUT_MS", "30000"))
    )
    
    # Agent configuration
    agents = AgentConfig(
        timeout_ms=int(os.getenv("AGENT_TIMEOUT_MS", "45000")),
        max_retries=int(os.getenv("AGENT_MAX_RETRIES", "3")),
        enable_mvp_agents=os.getenv("ENABLE_MVP_AGENTS", "true").lower() == "true",
        enable_event_intelligence=os.getenv("ENABLE_EVENT_INTELLIGENCE", "true").lower() == "true",
        enable_polling_statistical=os.getenv("ENABLE_POLLING_STATISTICAL", "true").lower() == "true",
        enable_sentiment_narrative=os.getenv("ENABLE_SENTIMENT_NARRATIVE", "true").lower() == "true",
        enable_price_action=os.getenv("ENABLE_PRICE_ACTION", "true").lower() == "true",
        enable_event_scenario=os.getenv("ENABLE_EVENT_SCENARIO", "true").lower() == "true"
    )
    
    # Consensus configuration
    consensus = ConsensusConfig(
        min_agents_required=int(os.getenv("CONSENSUS_MIN_AGENTS", "3")),
        disagreement_threshold=float(os.getenv("CONSENSUS_DISAGREEMENT_THRESHOLD", "0.15")),
        confidence_band_multiplier=float(os.getenv("CONSENSUS_CONFIDENCE_BAND_MULTIPLIER", "1.96")),
        min_edge_threshold=float(os.getenv("MIN_EDGE_THRESHOLD", "0.05"))
    )
    
    # Database configuration
    database = DatabaseConfig(
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_key=os.getenv("SUPABASE_KEY"),
        postgres_connection_string=os.getenv("POSTGRES_CONNECTION_STRING"),
        enable_persistence=os.getenv("ENABLE_PERSISTENCE", "true").lower() == "true"
    )
    
    # Memory system configuration
    memory_system = MemorySystemConfig(
        enable_memory=os.getenv("ENABLE_MEMORY", "true").lower() == "true",
        max_historical_signals=int(os.getenv("MAX_HISTORICAL_SIGNALS", "3")),
        memory_timeout_ms=int(os.getenv("MEMORY_TIMEOUT_MS", "5000"))
    )
    
    return EngineConfig(
        polymarket=polymarket,
        langgraph=langgraph,
        opik=opik,
        llm=llm,
        agents=agents,
        consensus=consensus,
        database=database,
        memory_system=memory_system
    )
