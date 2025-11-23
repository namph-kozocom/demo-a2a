"""Base Agent class"""


class BaseAgent:
    """Base class for all agents - provides common agent name storage"""
    
    def __init__(self, name: str):
        self.name = name
