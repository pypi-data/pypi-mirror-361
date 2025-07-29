"""
A beautiful terminal chat interface for OpenAI agents.

Usage:
    from repl_chat import start_chat
    from agents import Agent
    
    agent = Agent(name="My Assistant", instructions="You are a helpful assistant.")
    start_chat(agent)
"""

from .chat import start_chat
from .dspy_chat import start_dspy_chat

__all__ = ["start_chat", "start_dspy_chat"]
__version__ = "0.2.0" 