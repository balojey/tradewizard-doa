"""LLM factory for creating Gradient AI instances with Opik integration."""

import logging
from typing import Optional, Type, TypeVar
from pydantic import BaseModel

from langchain_gradient import ChatGradient
from langchain_core.language_models import BaseChatModel

from config import EngineConfig, LLMConfig

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


def create_llm_instance(
    config: LLMConfig,
    opik_config: Optional[dict] = None,
    structured_output_model: Optional[Type[T]] = None
) -> BaseChatModel:
    """
    Create a Gradient AI LLM instance with optional structured output and Opik tracing.
    
    Args:
        config: LLM configuration with model name, temperature, etc.
        opik_config: Optional Opik callback configuration for tracing
        structured_output_model: Optional Pydantic model for structured output
        
    Returns:
        Configured ChatGradient instance, optionally with structured output
        
    Example:
        >>> from models.types import AgentSignal
        >>> llm = create_llm_instance(
        ...     config=engine_config.llm,
        ...     opik_config={"project_name": "tradewizard"},
        ...     structured_output_model=AgentSignal
        ... )
    """
    try:
        # Create base ChatGradient instance
        llm = ChatGradient(
            model=config.model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            timeout=config.timeout_ms / 1000,  # Convert ms to seconds
        )
        
        logger.info(
            f"Created ChatGradient instance: model={config.model_name}, "
            f"temperature={config.temperature}, max_tokens={config.max_tokens}"
        )
        
        # Add Opik callback if configured
        if opik_config:
            try:
                from opik.integrations.langchain import OpikTracer
                
                tracer = OpikTracer(
                    project_name=opik_config.get("project_name", "tradewizard-doa"),
                    tags=opik_config.get("tags", [])
                )
                
                # Attach tracer to LLM
                llm.callbacks = [tracer]
                
                logger.info(
                    f"Attached Opik tracer: project={opik_config.get('project_name')}"
                )
            except ImportError:
                logger.warning(
                    "Opik not available, skipping tracing integration. "
                    "Install with: pip install opik"
                )
            except Exception as e:
                logger.warning(f"Failed to initialize Opik tracer: {e}")
        
        # Add structured output if model provided
        if structured_output_model:
            llm = llm.with_structured_output(structured_output_model)
            logger.info(
                f"Configured structured output: {structured_output_model.__name__}"
            )
        
        return llm
        
    except Exception as e:
        logger.error(f"Failed to create LLM instance: {e}")
        raise


def create_agent_llm(
    config: EngineConfig,
    agent_name: str,
    output_model: Type[T]
) -> BaseChatModel:
    """
    Create an LLM instance specifically configured for an agent.
    
    This is a convenience wrapper around create_llm_instance that:
    - Uses the engine's LLM configuration
    - Adds Opik tracing with agent-specific tags
    - Configures structured output for the agent's signal type
    
    Args:
        config: Engine configuration
        agent_name: Name of the agent (for tracing tags)
        output_model: Pydantic model for agent output (e.g., AgentSignal)
        
    Returns:
        Configured LLM instance ready for agent use
        
    Example:
        >>> from models.types import AgentSignal
        >>> llm = create_agent_llm(
        ...     config=engine_config,
        ...     agent_name="market_microstructure",
        ...     output_model=AgentSignal
        ... )
    """
    opik_config = None
    if config.opik.enable_tracing:
        opik_config = {
            "project_name": config.opik.project_name,
            "tags": ["agent", agent_name]
        }
    
    return create_llm_instance(
        config=config.llm,
        opik_config=opik_config,
        structured_output_model=output_model
    )

