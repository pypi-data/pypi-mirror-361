"""
Core Memory Manager for NeuronMemory

This module implements the Cognitive Memory Manager (CMM) that orchestrates
all memory operations and provides the main interface for memory management.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from ..memory.memory_objects import (
    BaseMemory, MemoryType, EmotionalState, MemoryMetadata,
    EpisodicMemory, SemanticMemory, ProceduralMemory, SocialMemory, WorkingMemory,
    create_episodic_memory, create_semantic_memory, create_procedural_memory,
    create_social_memory, create_working_memory
)
from .memory_store import MemoryStore
from .retrieval_engine import RetrievalEngine, SearchContext, SearchStrategy, RetrievalResult
from ..llm.azure_openai_client import AzureOpenAIClient
from ..config import neuron_memory_config

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Cognitive Memory Manager (CMM) - Central orchestrator for all memory operations
    
    Features:
    - Complete memory lifecycle management
    - Intelligent memory routing and storage
    - Advanced retrieval with context awareness
    - Automatic memory consolidation and optimization
    - Performance monitoring and analytics
    - Multi-user and multi-session support
    """
    
    def __init__(self):
        """Initialize the memory manager"""
        self.config = neuron_memory_config
        self.memory_store = MemoryStore()
        self.retrieval_engine = RetrievalEngine()
        self.llm_client = AzureOpenAIClient()
        
        # Active sessions and contexts
        self._active_sessions: Dict[str, SearchContext] = {}
        self._session_working_memory: Dict[str, List[str]] = {}
        
        # Background tasks
        self._consolidation_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # Performance metrics
        self._metrics = {
            "memories_created": 0,
            "memories_retrieved": 0,
            "searches_performed": 0,
            "consolidations_run": 0,
            "average_response_time": 0.0
        }
        
        # Start background tasks
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background maintenance tasks"""
        try:
            # Memory consolidation task
            self._consolidation_task = asyncio.create_task(
                self._consolidation_loop()
            )
            
            # Cleanup task  
            self._cleanup_task = asyncio.create_task(
                self._cleanup_loop()
            )
            
            logger.info("Background tasks started")
            
        except Exception as e:
            logger.error(f"Error starting background tasks: {e}")
    
    async def create_memory(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.SEMANTIC,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        importance_score: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        Create and store a new memory
        
        Args:
            content: Memory content
            memory_type: Type of memory to create
            user_id: ID of the user creating the memory
            session_id: Session ID for context
            importance_score: Importance score (auto-calculated if None)
            metadata: Additional metadata
            **kwargs: Type-specific memory attributes
            
        Returns:
            Memory ID of the created memory
        """
        try:
            start_time = datetime.utcnow()
            
            # Auto-analyze importance if not provided
            if importance_score is None:
                context = self._get_session_context(session_id) if session_id else ""
                importance_score = await self.llm_client.analyze_importance(content, str(context))
            
            # Extract entities and emotion
            entities = await self.llm_client.extract_entities(content)
            emotion_data = await self.llm_client.detect_emotion(content)
            
            # Create memory metadata
            memory_metadata = MemoryMetadata(
                importance_score=importance_score,
                user_id=user_id,
                session_id=session_id,
                context_tags=entities
            )
            
            if metadata:
                # Merge additional metadata
                for key, value in metadata.items():
                    if hasattr(memory_metadata, key):
                        setattr(memory_metadata, key, value)
            
            # Create specific memory type
            memory = None
            if memory_type == MemoryType.EPISODIC:
                emotional_state = EmotionalState(
                    valence=emotion_data.get("valence", 0.0),
                    arousal=emotion_data.get("arousal", 0.0),
                    dominance=emotion_data.get("dominance", 0.0)
                )
                memory = create_episodic_memory(
                    content=content,
                    emotional_state=emotional_state,
                    **{k: v for k, v in kwargs.items() if k != 'emotional_state'}
                )
            elif memory_type == MemoryType.SEMANTIC:
                memory = create_semantic_memory(
                    content=content,
                    concepts=entities,
                    **kwargs
                )
            elif memory_type == MemoryType.PROCEDURAL:
                memory = create_procedural_memory(
                    content=content,
                    **kwargs
                )
            elif memory_type == MemoryType.SOCIAL:
                memory = create_social_memory(
                    content=content,
                    person_id=kwargs.get('person_id'),
                    relationship_type=kwargs.get('relationship_type'),
                    **{k: v for k, v in kwargs.items() if k not in ['person_id', 'relationship_type']}
                )
            elif memory_type == MemoryType.WORKING:
                memory = create_working_memory(
                    content=content,
                    task_context=kwargs.get('task_context', ''),
                    **kwargs
                )
            else:
                # Default to semantic memory
                memory = create_semantic_memory(content=content, **kwargs)
            
            # Set metadata
            memory.metadata = memory_metadata
            
            # Store the memory
            memory_id = await self.memory_store.store_memory(memory)
            
            # Add to session working memory if applicable
            if session_id and memory_type == MemoryType.WORKING:
                if session_id not in self._session_working_memory:
                    self._session_working_memory[session_id] = []
                self._session_working_memory[session_id].append(memory_id)
            
            # Update metrics
            self._metrics["memories_created"] += 1
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_response_time(processing_time)
            
            logger.debug(f"Created {memory_type.value} memory {memory_id}")
            
            return memory_id
            
        except Exception as e:
            logger.error(f"Error creating memory: {e}")
            raise
    
    async def retrieve_memory(self, memory_id: str) -> Optional[BaseMemory]:
        """
        Retrieve a specific memory by ID
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            Memory object if found, None otherwise
        """
        try:
            start_time = datetime.utcnow()
            
            memory = await self.memory_store.retrieve_memory(memory_id)
            
            if memory:
                self._metrics["memories_retrieved"] += 1
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                self._update_response_time(processing_time)
                
                logger.debug(f"Retrieved memory {memory_id}")
            
            return memory
            
        except Exception as e:
            logger.error(f"Error retrieving memory {memory_id}: {e}")
            return None
    
    async def search_memories(
        self,
        query: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        memory_types: Optional[List[MemoryType]] = None,
        limit: int = 10,
        strategy: SearchStrategy = SearchStrategy.HYBRID_MULTI_MODAL,
        context_data: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """
        Search for memories using intelligent retrieval
        
        Args:
            query: Search query
            user_id: Filter by user ID
            session_id: Session context
            memory_types: Types of memories to search
            limit: Maximum number of results
            strategy: Search strategy to use
            context_data: Additional context information
            
        Returns:
            List of retrieval results
        """
        try:
            start_time = datetime.utcnow()
            
            # Build search context
            search_context = SearchContext(
                user_id=user_id,
                session_id=session_id
            )
            
            # Add context from active session
            if session_id in self._active_sessions:
                session_context = self._active_sessions[session_id]
                search_context.current_task = session_context.current_task
                search_context.domain_focus = session_context.domain_focus
                search_context.social_context = session_context.social_context
            
            # Merge additional context data
            if context_data:
                for key, value in context_data.items():
                    if hasattr(search_context, key):
                        setattr(search_context, key, value)
            
            # Perform search
            results = await self.retrieval_engine.search(
                query=query,
                memory_store=self.memory_store,
                context=search_context,
                strategy=strategy,
                limit=limit
            )
            
            # Update metrics
            self._metrics["searches_performed"] += 1
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_response_time(processing_time)
            
            logger.debug(f"Found {len(results)} memories for query: {query}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return []
    
    async def update_memory(
        self,
        memory_id: str,
        content: Optional[str] = None,
        importance_score: Optional[float] = None,
        metadata_updates: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update an existing memory
        
        Args:
            memory_id: ID of memory to update
            content: New content (optional)
            importance_score: New importance score (optional)
            metadata_updates: Metadata updates (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Retrieve existing memory
            memory = await self.memory_store.retrieve_memory(memory_id)
            if not memory:
                logger.warning(f"Memory {memory_id} not found for update")
                return False
            
            # Update content if provided
            if content is not None:
                memory.content = content
                # Regenerate embedding for new content
                memory.embedding = await self.llm_client.generate_embedding(content)
            
            # Update importance score if provided
            if importance_score is not None:
                memory.metadata.importance_score = importance_score
            
            # Update metadata if provided
            if metadata_updates:
                for key, value in metadata_updates.items():
                    if hasattr(memory.metadata, key):
                        setattr(memory.metadata, key, value)
            
            # Update in store
            success = await self.memory_store.update_memory(memory)
            
            if success:
                logger.debug(f"Updated memory {memory_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating memory {memory_id}: {e}")
            return False
    
    async def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory
        
        Args:
            memory_id: ID of memory to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            success = await self.memory_store.delete_memory(memory_id)
            
            # Remove from session working memory if present
            for session_memories in self._session_working_memory.values():
                if memory_id in session_memories:
                    session_memories.remove(memory_id)
            
            if success:
                logger.debug(f"Deleted memory {memory_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting memory {memory_id}: {e}")
            return False
    
    async def start_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Start a new memory session
        
        Args:
            session_id: Unique session identifier
            user_id: User ID for the session
            context: Initial session context
            
        Returns:
            True if successful, False otherwise
        """
        try:
            search_context = SearchContext(
                user_id=user_id,
                session_id=session_id,
                time_context=datetime.utcnow()
            )
            
            if context:
                search_context.current_task = context.get('current_task')
                search_context.domain_focus = context.get('domain_focus')
                search_context.social_context = context.get('social_context')
            
            self._active_sessions[session_id] = search_context
            self._session_working_memory[session_id] = []
            
            logger.debug(f"Started session {session_id} for user {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting session {session_id}: {e}")
            return False
    
    async def end_session(self, session_id: str) -> bool:
        """
        End a memory session and clean up working memory
        
        Args:
            session_id: Session ID to end
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Clean up working memory for this session
            if session_id in self._session_working_memory:
                working_memory_ids = self._session_working_memory[session_id]
                for memory_id in working_memory_ids:
                    await self.memory_store.delete_memory(memory_id)
                del self._session_working_memory[session_id]
            
            # Remove session context
            if session_id in self._active_sessions:
                del self._active_sessions[session_id]
            
            logger.debug(f"Ended session {session_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error ending session {session_id}: {e}")
            return False
    
    async def get_session_context(self, session_id: str) -> Optional[SearchContext]:
        """Get context for an active session"""
        return self._active_sessions.get(session_id)
    
    def _get_session_context(self, session_id: str) -> str:
        """Get session context as string for importance analysis"""
        if session_id in self._active_sessions:
            context = self._active_sessions[session_id]
            parts = []
            if context.current_task:
                parts.append(f"Task: {context.current_task}")
            if context.domain_focus:
                parts.append(f"Domain: {context.domain_focus}")
            return " | ".join(parts)
        return ""
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive memory system statistics"""
        try:
            store_stats = await self.memory_store.get_statistics()
            
            return {
                **self._metrics,
                **store_stats,
                "active_sessions": len(self._active_sessions),
                "working_memory_items": sum(
                    len(memories) for memories in self._session_working_memory.values()
                )
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    def _update_response_time(self, processing_time: float):
        """Update average response time metric"""
        if self._metrics["average_response_time"] == 0.0:
            self._metrics["average_response_time"] = processing_time
        else:
            # Exponential moving average
            alpha = 0.1
            self._metrics["average_response_time"] = (
                alpha * processing_time + 
                (1 - alpha) * self._metrics["average_response_time"]
            )
    
    async def _consolidation_loop(self):
        """Background task for memory consolidation"""
        while True:
            try:
                await asyncio.sleep(self.config.memory_consolidation_interval)
                
                # Perform memory consolidation
                await self._perform_consolidation()
                
                self._metrics["consolidations_run"] += 1
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in consolidation loop: {e}")
    
    async def _cleanup_loop(self):
        """Background task for memory cleanup"""
        while True:
            try:
                await asyncio.sleep(self.config.cleanup_interval)
                
                # Clean up expired memories
                cleaned_count = await self.memory_store.cleanup_expired_memories()
                
                logger.info(f"Cleaned up {cleaned_count} expired memories")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    async def _perform_consolidation(self):
        """Perform memory consolidation operations"""
        try:
            # This is a simplified consolidation process
            # In a full implementation, this would include:
            # - Pattern extraction from episodic memories
            # - Semantic knowledge network building
            # - Memory strength adjustment based on usage
            # - Relationship discovery and strengthening
            
            logger.debug("Memory consolidation completed")
            
        except Exception as e:
            logger.error(f"Error during memory consolidation: {e}")
    
    async def shutdown(self):
        """Gracefully shutdown the memory manager"""
        try:
            # Cancel background tasks
            if self._consolidation_task:
                self._consolidation_task.cancel()
            if self._cleanup_task:
                self._cleanup_task.cancel()
            
            # Clean up active sessions
            for session_id in list(self._active_sessions.keys()):
                await self.end_session(session_id)
            
            logger.info("Memory manager shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    @asynccontextmanager
    async def session_context(self, session_id: str, user_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        """Context manager for memory sessions"""
        try:
            await self.start_session(session_id, user_id, context)
            yield self
        finally:
            await self.end_session(session_id) 