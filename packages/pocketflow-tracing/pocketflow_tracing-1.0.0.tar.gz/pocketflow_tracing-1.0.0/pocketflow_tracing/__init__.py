"""
PocketFlow Tracing Package

A comprehensive observability package for PocketFlow workflows using Langfuse.
Provides decorator-based tracing with minimal code changes, focusing on node execution
with automatic input/output data tracing.

Features:
- Automatic tracing of PocketFlow workflows
- Node-level observability (prep, exec, post phases)
- Input/output tracking
- Error tracking
- Async support
- Langfuse v2 SDK integration
- Environment variable configuration with python-dotenv

Example:
    ```python
    from pocketflow import Flow, Node
    from pocketflow_tracing import trace_flow
    
    @trace_flow()
    class MyFlow(Flow):
        def __init__(self):
            super().__init__(start=MyNode())
    ```
"""

from .config import TracingConfig
from .core import LangfuseTracer
from .decorator import trace_flow
from .utils import setup_tracing, test_langfuse_connection, print_configuration_help

__version__ = "1.0.0"
__author__ = "PocketFlow Team"
__email__ = "support@pocketflow.dev"
__description__ = "Observability and tracing for PocketFlow workflows using Langfuse"

__all__ = [
    "trace_flow",
    "TracingConfig",
    "LangfuseTracer",
    "setup_tracing",
    "test_langfuse_connection",
    "print_configuration_help",
]
