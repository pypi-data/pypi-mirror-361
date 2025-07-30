"""
Main API Interface for NeuronMemory

This module provides the primary public interface for the NeuronMemory system,
designed for easy integration with LLMs and AI agents.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from ..core.memory_manager import MemoryManager
from ..memory.memory_objects import MemoryType, BaseMemory
from ..core.retrieval_engine import SearchStrategy, RetrievalResult
from ..config import validate_config

logger = logging.getLogger(__name__)

class NeuronMemoryAPI:
    """
    Main API interface for NeuronMemory
    
    This class provides a simple, high-level interface for:
    - Creating and storing memories
    - Searching and retrieving memories
    - Managing memory sessions
    - Getting system insights and analytics
    """
    
    def __init__(self):
        """Initialize the NeuronMemory API"""
        # Validate configuration
        if not validate_config():
            raise ValueError("Invalid configuration. Please check your .env file.")
        
        self.memory_manager = MemoryManager()
        self._initialized = True
        
        logger.info("NeuronMemory API initialized successfully")
    
    async def create_memory(
        self,
        content: str,
        memory_type: str = "semantic",
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        importance: Optional[float] = None,
        **metadata
    ) -> str:
        """
        Create a new memory
        
        Args:
            content: The content to remember
            memory_type: Type of memory ("semantic", "episodic", "procedural", "social", "working")
            user_id: User identifier
            session_id: Session identifier
            importance: Importance score (0.0-1.0, auto-calculated if None)
            **metadata: Additional metadata fields
            
        Returns:
            Memory ID of the created memory
            
        Example:
            memory_id = await api.create_memory(
                "The user prefers morning meetings",
                memory_type="social",
                user_id="user123",
                person_id="user123",
                relationship_type="colleague"
            )
        """
        try:
            # Convert string to MemoryType enum
            memory_type_enum = MemoryType(memory_type.lower())
            
            memory_id = await self.memory_manager.create_memory(
                content=content,
                memory_type=memory_type_enum,
                user_id=user_id,
                session_id=session_id,
                importance_score=importance,
                **metadata
            )
            
            return memory_id
            
        except Exception as e:
            logger.error(f"Error creating memory: {e}")
            raise
    
    async def search_memories(
        self,
        query: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        memory_types: Optional[List[str]] = None,
        limit: int = 10,
        min_relevance: float = 0.1
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant memories
        
        Args:
            query: Search query text
            user_id: Filter by user ID
            session_id: Session context
            memory_types: Types of memories to search
            limit: Maximum number of results
            min_relevance: Minimum relevance score (0.0-1.0)
            
        Returns:
            List of memory results with content and scores
            
        Example:
            results = await api.search_memories(
                "user preferences for meetings",
                user_id="user123",
                limit=5
            )
        """
        try:
            # Convert string memory types to enums
            memory_type_enums = None
            if memory_types:
                memory_type_enums = [MemoryType(mt.lower()) for mt in memory_types]
            
            results = await self.memory_manager.search_memories(
                query=query,
                user_id=user_id,
                session_id=session_id,
                memory_types=memory_type_enums,
                limit=limit
            )
            
            # Convert results to dictionary format
            formatted_results = []
            for result in results:
                if result.final_score >= min_relevance:
                    formatted_results.append({
                        "memory_id": result.memory.memory_id,
                        "content": result.memory.content,
                        "memory_type": result.memory.memory_type.value,
                        "relevance_score": result.final_score,
                        "similarity_score": result.similarity_score,
                        "importance_score": result.importance_score,
                        "created_at": result.memory.metadata.created_at.isoformat(),
                        "explanation": result.explanation,
                        "user_id": result.memory.metadata.user_id,
                        "session_id": result.memory.metadata.session_id,
                        "context_tags": result.memory.metadata.context_tags
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return []
    
    async def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific memory by ID
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            Memory data as dictionary, or None if not found
        """
        try:
            memory = await self.memory_manager.retrieve_memory(memory_id)
            
            if memory:
                return {
                    "memory_id": memory.memory_id,
                    "content": memory.content,
                    "memory_type": memory.memory_type.value,
                    "importance_score": memory.metadata.importance_score,
                    "confidence_score": memory.metadata.confidence_score,
                    "created_at": memory.metadata.created_at.isoformat(),
                    "last_accessed": memory.metadata.last_accessed.isoformat(),
                    "access_count": memory.metadata.access_count,
                    "user_id": memory.metadata.user_id,
                    "session_id": memory.metadata.session_id,
                    "source": memory.metadata.source,
                    "context_tags": memory.metadata.context_tags
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving memory {memory_id}: {e}")
            return None
    
    async def create_episodic_memory(
        self,
        content: str,
        participants: Optional[List[str]] = None,
        location: Optional[str] = None,
        emotions: Optional[Dict[str, float]] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> str:
        """
        Create an episodic memory (experience/event)
        
        Args:
            content: Description of the experience
            participants: List of people involved
            location: Where it happened
            emotions: Emotional context {"valence": 0.5, "arousal": 0.3, "dominance": 0.7}
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            Memory ID
        """
        metadata = {}
        if participants:
            metadata["participants"] = participants
        if location:
            metadata["location"] = location
        if emotions:
            metadata["emotional_state"] = emotions
        
        return await self.create_memory(
            content=content,
            memory_type="episodic",
            user_id=user_id,
            session_id=session_id,
            **metadata
        )
    
    async def create_social_memory(
        self,
        content: str,
        person_id: str,
        relationship_type: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> str:
        """
        Create a social memory (about relationships and people)
        
        Args:
            content: Information about the person or relationship
            person_id: Identifier for the person
            relationship_type: Type of relationship (colleague, friend, family, etc.)
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            Memory ID
        """
        return await self.create_memory(
            content=content,
            memory_type="social",
            user_id=user_id,
            session_id=session_id,
            person_id=person_id,
            relationship_type=relationship_type
        )
    
    async def start_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        task: Optional[str] = None,
        domain: Optional[str] = None
    ) -> bool:
        """
        Start a memory session for context-aware operations
        
        Args:
            session_id: Unique session identifier
            user_id: User identifier
            task: Current task description
            domain: Domain of focus
            
        Returns:
            True if successful
        """
        try:
            context = {}
            if task:
                context["current_task"] = task
            if domain:
                context["domain_focus"] = domain
            
            return await self.memory_manager.start_session(
                session_id=session_id,
                user_id=user_id,
                context=context
            )
            
        except Exception as e:
            logger.error(f"Error starting session {session_id}: {e}")
            return False
    
    async def end_session(self, session_id: str) -> bool:
        """
        End a memory session
        
        Args:
            session_id: Session identifier to end
            
        Returns:
            True if successful
        """
        try:
            return await self.memory_manager.end_session(session_id)
            
        except Exception as e:
            logger.error(f"Error ending session {session_id}: {e}")
            return False
    
    async def get_context_for_llm(
        self,
        query: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        max_context_length: int = 2000
    ) -> str:
        """
        Get relevant memory context formatted for LLM consumption
        
        Args:
            query: Current query or context
            user_id: User identifier
            session_id: Session identifier
            max_context_length: Maximum context length in characters
            
        Returns:
            Formatted context string for LLM
        """
        try:
            # Search for relevant memories
            results = await self.search_memories(
                query=query,
                user_id=user_id,
                session_id=session_id,
                limit=10,
                min_relevance=0.3
            )
            
            if not results:
                return ""
            
            # Format context for LLM
            context_parts = ["[RELEVANT MEMORIES]"]
            current_length = len(context_parts[0])
            
            for result in results:
                memory_text = f"\n- {result['content']} (relevance: {result['relevance_score']:.2f})"
                
                if current_length + len(memory_text) > max_context_length:
                    break
                
                context_parts.append(memory_text)
                current_length += len(memory_text)
            
            context_parts.append("\n[END MEMORIES]")
            
            return "".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error getting LLM context: {e}")
            return ""
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get system statistics and health metrics
        
        Returns:
            Dictionary with system statistics
        """
        try:
            return await self.memory_manager.get_statistics()
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    def is_healthy(self) -> bool:
        """Check if the memory system is healthy and operational"""
        return self._initialized and self.memory_manager is not None 