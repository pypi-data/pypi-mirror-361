"""
Development-Only Weave Tracer for Agentic Orchestration

This module provides optional Weave tracing for development and debugging
of the agentic orchestration flow. It's designed to be:

1. Development-only: Not included in production builds
2. Optional: Works without Weave installed
3. Non-intrusive: Doesn't affect core functionality
4. Detailed: Provides comprehensive tracing of agent interactions

Usage:
    # Enable in development
    export AGENT_SENTINEL_DEV_MODE=true
    export WEAVE_API_KEY=your-key
    
    # Trace agentic flow
    tracer = DevWeaveTracer()
    with tracer.trace_orchestration(event):
        result = await orchestrator.orchestrate_security_analysis(event)
"""

import os
import time
import logging
from contextlib import asynccontextmanager, contextmanager
from typing import Dict, Any, Optional, AsyncGenerator, Generator
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Check if we're in development mode
DEV_MODE = os.getenv('AGENT_SENTINEL_DEV_MODE', 'false').lower() == 'true'
WEAVE_AVAILABLE = False

# Try to import Weave only in dev mode
if DEV_MODE:
    try:
        import weave
        WEAVE_AVAILABLE = True
        logger.info("Weave available for development tracing")
    except ImportError:
        logger.info("Weave not available - tracing disabled")
else:
    logger.debug("Not in development mode - Weave tracing disabled")


@dataclass
class TraceContext:
    """Context for tracing operations."""
    trace_id: str
    operation_name: str
    start_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_trace: Optional['TraceContext'] = None


class DevWeaveTracer:
    """
    Development-only Weave tracer for agentic orchestration.
    
    This tracer provides detailed insights into the agentic flow:
    - Agent interactions and handoffs
    - LLM calls and responses
    - Processing times and performance
    - Error handling and recovery
    
    Only active in development mode with Weave installed.
    """
    
    def __init__(self):
        self.enabled = DEV_MODE and WEAVE_AVAILABLE
        self.initialized = False
        self.active_traces: Dict[str, TraceContext] = {}
        
        if self.enabled:
            self._initialize_weave()
    
    def _initialize_weave(self):
        """Initialize Weave for development tracing."""
        try:
            if not self.initialized:
                weave.init(project_name="agent-sentinel-dev")
                self.initialized = True
                logger.info("Weave initialized for development tracing")
        except Exception as e:
            logger.warning(f"Failed to initialize Weave: {e}")
            self.enabled = False
    
    @asynccontextmanager
    async def trace_orchestration(self, event) -> AsyncGenerator[Optional[Dict[str, Any]], None]:
        """
        Trace the complete agentic orchestration flow.
        
        Args:
            event: Security event being processed
            
        Yields:
            Trace context for the orchestration
        """
        if not self.enabled:
            yield None
            return
        
        trace_id = f"orchestration_{int(time.time() * 1000)}"
        
        try:
            # Start orchestration trace
            with weave.attributes({
                "operation": "agentic_orchestration",
                "event_type": event.threat_type.value,
                "event_severity": event.severity.value,
                "event_confidence": event.confidence,
                "agent_id": event.agent_id,
                "trace_id": trace_id
            }):
                start_time = time.time()
                
                trace_context = TraceContext(
                    trace_id=trace_id,
                    operation_name="orchestration",
                    start_time=start_time,
                    metadata={
                        "event_type": event.threat_type.value,
                        "severity": event.severity.value,
                        "confidence": event.confidence
                    }
                )
                
                self.active_traces[trace_id] = trace_context
                
                logger.info(f"Started orchestration trace: {trace_id}")
                
                yield {"trace_id": trace_id, "context": trace_context}
                
                # Log completion
                processing_time = time.time() - start_time
                logger.info(f"Completed orchestration trace: {trace_id} in {processing_time:.2f}s")
                
        except Exception as e:
            logger.error(f"Orchestration trace failed: {e}")
            yield None
        finally:
            # Clean up trace
            if trace_id in self.active_traces:
                del self.active_traces[trace_id]
    
    @contextmanager
    def trace_agent_call(self, agent_role: str, operation: str, parent_trace_id: Optional[str] = None) -> Generator[Optional[Dict[str, Any]], None, None]:
        """
        Trace individual agent calls within the orchestration.
        
        Args:
            agent_role: Role of the agent (threat_analyst, intelligence_agent, etc.)
            operation: Specific operation being performed
            parent_trace_id: Parent orchestration trace ID
            
        Yields:
            Trace context for the agent call
        """
        if not self.enabled:
            yield None
            return
        
        trace_id = f"{agent_role}_{operation}_{int(time.time() * 1000)}"
        
        try:
            with weave.attributes({
                "operation": f"agent_call_{agent_role}",
                "agent_role": agent_role,
                "agent_operation": operation,
                "parent_trace": parent_trace_id,
                "trace_id": trace_id
            }):
                start_time = time.time()
                
                trace_context = TraceContext(
                    trace_id=trace_id,
                    operation_name=f"{agent_role}_{operation}",
                    start_time=start_time,
                    metadata={
                        "agent_role": agent_role,
                        "operation": operation,
                        "parent_trace": parent_trace_id
                    }
                )
                
                self.active_traces[trace_id] = trace_context
                
                logger.debug(f"Started agent trace: {trace_id}")
                
                yield {"trace_id": trace_id, "context": trace_context}
                
                # Log completion
                processing_time = time.time() - start_time
                logger.debug(f"Completed agent trace: {trace_id} in {processing_time:.2f}s")
                
        except Exception as e:
            logger.error(f"Agent trace failed: {e}")
            yield None
        finally:
            # Clean up trace
            if trace_id in self.active_traces:
                del self.active_traces[trace_id]
    
    def trace_llm_call(self, agent_role: str, prompt_type: str, model: str, parent_trace_id: Optional[str] = None):
        """
        Trace LLM calls made by agents.
        
        Args:
            agent_role: Role of the agent making the call
            prompt_type: Type of prompt (analysis, intelligence, report)
            model: LLM model being used
            parent_trace_id: Parent agent trace ID
            
        Returns:
            Decorator for LLM calls
        """
        def decorator(func):
            async def wrapper(*args, **kwargs):
                if not self.enabled:
                    return await func(*args, **kwargs)
                
                trace_id = f"llm_{agent_role}_{prompt_type}_{int(time.time() * 1000)}"
                
                try:
                    with weave.attributes({
                        "operation": "llm_call",
                        "agent_role": agent_role,
                        "prompt_type": prompt_type,
                        "model": model,
                        "parent_trace": parent_trace_id,
                        "trace_id": trace_id
                    }):
                        start_time = time.time()
                        
                        logger.debug(f"Started LLM trace: {trace_id}")
                        
                        # Call the actual LLM function
                        result = await func(*args, **kwargs)
                        
                        # Log completion with metrics
                        processing_time = time.time() - start_time
                        
                        # Extract token usage if available
                        token_usage = {}
                        if hasattr(result, 'usage'):
                            token_usage = {
                                "prompt_tokens": result.usage.prompt_tokens,
                                "completion_tokens": result.usage.completion_tokens,
                                "total_tokens": result.usage.total_tokens
                            }
                        
                        logger.debug(f"Completed LLM trace: {trace_id} in {processing_time:.2f}s")
                        
                        return result
                        
                except Exception as e:
                    logger.error(f"LLM trace failed: {e}")
                    # Still execute the function even if tracing fails
                    return await func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    def log_agent_handoff(self, from_agent: str, to_agent: str, data_summary: str, trace_id: Optional[str] = None):
        """
        Log handoffs between agents in the orchestration.
        
        Args:
            from_agent: Agent passing data
            to_agent: Agent receiving data
            data_summary: Summary of data being passed
            trace_id: Associated trace ID
        """
        if not self.enabled:
            return
        
        try:
            with weave.attributes({
                "operation": "agent_handoff",
                "from_agent": from_agent,
                "to_agent": to_agent,
                "data_summary": data_summary,
                "trace_id": trace_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }):
                logger.info(f"Agent handoff: {from_agent} → {to_agent}")
                
        except Exception as e:
            logger.error(f"Failed to log agent handoff: {e}")
    
    def log_orchestration_metrics(self, metrics: Dict[str, Any], trace_id: Optional[str] = None):
        """
        Log orchestration performance metrics.
        
        Args:
            metrics: Performance metrics dictionary
            trace_id: Associated trace ID
        """
        if not self.enabled:
            return
        
        try:
            with weave.attributes({
                "operation": "orchestration_metrics",
                "metrics": metrics,
                "trace_id": trace_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }):
                logger.info(f"Orchestration metrics logged for trace: {trace_id}")
                
        except Exception as e:
            logger.error(f"Failed to log orchestration metrics: {e}")
    
    def get_trace_summary(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """
        Get summary of a trace.
        
        Args:
            trace_id: Trace ID to summarize
            
        Returns:
            Trace summary or None if not found
        """
        if not self.enabled or trace_id not in self.active_traces:
            return None
        
        trace = self.active_traces[trace_id]
        return {
            "trace_id": trace.trace_id,
            "operation": trace.operation_name,
            "start_time": trace.start_time,
            "duration": time.time() - trace.start_time,
            "metadata": trace.metadata
        }
    
    def is_enabled(self) -> bool:
        """Check if tracing is enabled."""
        return self.enabled
    
    def get_active_traces(self) -> Dict[str, Dict[str, Any]]:
        """Get all active traces."""
        if not self.enabled:
            return {}
        
        summaries = {}
        for trace_id in self.active_traces:
            summary = self.get_trace_summary(trace_id)
            if summary:
                summaries[trace_id] = summary
        return summaries


# Global tracer instance for development
dev_tracer = DevWeaveTracer()


def get_dev_tracer() -> DevWeaveTracer:
    """Get the global development tracer instance."""
    return dev_tracer


# Convenience functions for easy usage
def trace_orchestration(event):
    """Convenience function to trace orchestration."""
    return dev_tracer.trace_orchestration(event)


def trace_agent_call(agent_role: str, operation: str, parent_trace_id: Optional[str] = None):
    """Convenience function to trace agent calls."""
    return dev_tracer.trace_agent_call(agent_role, operation, parent_trace_id)


def trace_llm_call(agent_role: str, prompt_type: str, model: str, parent_trace_id: Optional[str] = None):
    """Convenience function to trace LLM calls."""
    return dev_tracer.trace_llm_call(agent_role, prompt_type, model, parent_trace_id)


def log_agent_handoff(from_agent: str, to_agent: str, data_summary: str, trace_id: Optional[str] = None):
    """Convenience function to log agent handoffs."""
    dev_tracer.log_agent_handoff(from_agent, to_agent, data_summary, trace_id)


def log_orchestration_metrics(metrics: Dict[str, Any], trace_id: Optional[str] = None):
    """Convenience function to log orchestration metrics."""
    dev_tracer.log_orchestration_metrics(metrics, trace_id) 