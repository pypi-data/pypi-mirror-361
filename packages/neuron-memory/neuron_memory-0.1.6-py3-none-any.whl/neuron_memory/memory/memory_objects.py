"""
Core memory object definitions for NeuronMemory

This module defines the various types of memory objects that can be stored
and retrieved by the NeuronMemory system.
"""

from typing import Dict, List, Optional, Any, Union, Literal
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field
import uuid
import json

class MemoryType(str, Enum):
    """Enumeration of memory types"""
    WORKING = "working"
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    SOCIAL = "social"

class ImportanceLevel(str, Enum):
    """Memory importance levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"

class EmotionalState(BaseModel):
    """Emotional context for memories"""
    valence: float = Field(0.0, ge=-1.0, le=1.0, description="Positive/negative emotion (-1 to 1)")
    arousal: float = Field(0.0, ge=-1.0, le=1.0, description="Intensity of emotion (-1 to 1)")
    dominance: float = Field(0.0, ge=-1.0, le=1.0, description="Control/powerfulness (-1 to 1)")
    emotions: List[str] = Field(default_factory=list, description="Named emotions")

class MemoryMetadata(BaseModel):
    """Metadata for memory objects"""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    access_count: int = Field(default=0)
    importance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    source: Optional[str] = None
    context_tags: List[str] = Field(default_factory=list)
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class BaseMemory(BaseModel):
    """Base class for all memory objects"""
    memory_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    memory_type: MemoryType
    content: str
    metadata: MemoryMetadata = Field(default_factory=MemoryMetadata)
    embedding: Optional[List[float]] = None
    relationships: Dict[str, List[str]] = Field(default_factory=dict)
    
    def update_access(self):
        """Update access tracking"""
        self.metadata.last_accessed = datetime.utcnow()
        self.metadata.access_count += 1
    
    def calculate_decay(self) -> float:
        """Calculate memory decay based on age and access patterns"""
        now = datetime.utcnow()
        age_hours = (now - self.metadata.created_at).total_seconds() / 3600
        last_access_hours = (now - self.metadata.last_accessed).total_seconds() / 3600
        
        # Exponential decay with access frequency boost
        decay = 0.99 ** age_hours
        access_boost = min(1.0, self.metadata.access_count / 10.0)
        freshness_boost = 0.9 ** last_access_hours
        
        return decay * (1.0 + access_boost) * freshness_boost

class EpisodicMemory(BaseMemory):
    """Episodic memory for experiences and events"""
    memory_type: Literal[MemoryType.EPISODIC] = MemoryType.EPISODIC
    location: Optional[str] = None
    participants: List[str] = Field(default_factory=list)
    emotional_state: Optional[EmotionalState] = None
    sensory_details: Dict[str, Any] = Field(default_factory=dict)
    duration: Optional[timedelta] = None
    
class SemanticMemory(BaseMemory):
    """Semantic memory for facts and knowledge"""
    memory_type: Literal[MemoryType.SEMANTIC] = MemoryType.SEMANTIC
    domain: Optional[str] = None
    concepts: List[str] = Field(default_factory=list)
    relations: Dict[str, str] = Field(default_factory=dict)
    evidence: List[str] = Field(default_factory=list)
    certainty: float = Field(default=1.0, ge=0.0, le=1.0)

class ProceduralMemory(BaseMemory):
    """Procedural memory for skills and processes"""
    memory_type: Literal[MemoryType.PROCEDURAL] = MemoryType.PROCEDURAL
    steps: List[Dict[str, Any]] = Field(default_factory=list)
    conditions: Dict[str, Any] = Field(default_factory=dict)
    success_metrics: Dict[str, Any] = Field(default_factory=dict)
    skill_level: float = Field(default=0.0, ge=0.0, le=1.0)

class SocialMemory(BaseMemory):
    """Social memory for relationships and social contexts"""
    memory_type: Literal[MemoryType.SOCIAL] = MemoryType.SOCIAL
    person_id: str
    relationship_type: str
    personality_traits: Dict[str, float] = Field(default_factory=dict)
    communication_style: Dict[str, Any] = Field(default_factory=dict)
    interaction_history: List[Dict[str, Any]] = Field(default_factory=list)
    trust_level: float = Field(default=0.5, ge=0.0, le=1.0)

class WorkingMemory(BaseMemory):
    """Working memory for current active processing"""
    memory_type: Literal[MemoryType.WORKING] = MemoryType.WORKING
    task_context: str
    priority: float = Field(default=0.5, ge=0.0, le=1.0)
    expiration: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(hours=1))
    processing_status: str = Field(default="active")

class MemoryCluster(BaseModel):
    """Cluster of related memories"""
    cluster_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    memories: List[str] = Field(default_factory=list)  # Memory IDs
    cluster_type: str
    centroid_embedding: Optional[List[float]] = None
    coherence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class MemoryRelationship(BaseModel):
    """Relationship between memories"""
    relationship_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_memory_id: str
    target_memory_id: str
    relationship_type: str
    strength: float = Field(default=0.5, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Memory factory functions
def create_episodic_memory(
    content: str,
    participants: List[str] = None,
    location: str = None,
    emotional_state: EmotionalState = None,
    **kwargs
) -> EpisodicMemory:
    """Create an episodic memory"""
    return EpisodicMemory(
        content=content,
        participants=participants or [],
        location=location,
        emotional_state=emotional_state,
        **kwargs
    )

def create_semantic_memory(
    content: str,
    domain: str = None,
    concepts: List[str] = None,
    **kwargs
) -> SemanticMemory:
    """Create a semantic memory"""
    return SemanticMemory(
        content=content,
        domain=domain,
        concepts=concepts or [],
        **kwargs
    )

def create_procedural_memory(
    content: str,
    steps: List[Dict[str, Any]] = None,
    **kwargs
) -> ProceduralMemory:
    """Create a procedural memory"""
    return ProceduralMemory(
        content=content,
        steps=steps or [],
        **kwargs
    )

def create_social_memory(
    content: str,
    person_id: str,
    relationship_type: str,
    **kwargs
) -> SocialMemory:
    """Create a social memory"""
    return SocialMemory(
        content=content,
        person_id=person_id,
        relationship_type=relationship_type,
        **kwargs
    )

def create_working_memory(
    content: str,
    task_context: str,
    priority: float = 0.5,
    **kwargs
) -> WorkingMemory:
    """Create a working memory"""
    return WorkingMemory(
        content=content,
        task_context=task_context,
        priority=priority,
        **kwargs
    ) 