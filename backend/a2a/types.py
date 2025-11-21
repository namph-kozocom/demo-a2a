from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class AgentCapabilities:
    streaming: bool = False
    
@dataclass
class AgentSkill:
    id: str
    name: str
    description: str
    tags: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)

@dataclass
class AgentCard:
    name: str
    description: str
    url: str
    version: str
    default_input_modes: List[str]
    default_output_modes: List[str]
    capabilities: AgentCapabilities
    skills: List[AgentSkill]
    metadata: Dict[str, Any] = field(default_factory=dict)
