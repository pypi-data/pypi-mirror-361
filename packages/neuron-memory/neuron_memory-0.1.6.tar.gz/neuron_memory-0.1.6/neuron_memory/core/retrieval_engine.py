"""
Advanced Retrieval Engine (ARE) for NeuronMemory

This module implements intelligent memory retrieval with multi-modal search,
contextual ranking, and relevance optimization.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
from dataclasses import dataclass

from ..memory.memory_objects import BaseMemory, MemoryType, EmotionalState

from ..llm.azure_openai_client import AzureOpenAIClient
from ..config import neuron_memory_config

logger = logging.getLogger(__name__)

class SearchStrategy(str, Enum):
    """Search strategy types"""
    SEMANTIC_ONLY = "semantic_only"
    TEMPORAL_WEIGHTED = "temporal_weighted" 
    EMOTIONAL_FILTERED = "emotional_filtered"
    SOCIAL_CONTEXT = "social_context"
    HYBRID_MULTI_MODAL = "hybrid_multi_modal"

@dataclass
class SearchContext:
    """Context for memory search operations"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    current_task: Optional[str] = None
    emotional_state: Optional[EmotionalState] = None
    time_context: Optional[datetime] = None
    social_context: Optional[List[str]] = None
    domain_focus: Optional[str] = None
    urgency_level: float = 0.5

@dataclass
class RetrievalResult:
    """Result from memory retrieval"""
    memory: BaseMemory
    relevance_score: float
    similarity_score: float
    temporal_score: float
    importance_score: float
    context_score: float
    final_score: float
    explanation: str

class RetrievalEngine:
    """
    Advanced Retrieval Engine (ARE) for intelligent memory search
    
    Features:
    - Multi-modal search (semantic + temporal + emotional + social)
    - Context-aware ranking and relevance scoring
    - Adaptive search strategies based on query type
    - Diversity-aware result selection
    - Performance optimization with caching
    """
    
    def __init__(self):
        """Initialize the retrieval engine"""
        self.llm_client = AzureOpenAIClient()
        self.config = neuron_memory_config
        
        # Scoring weights for different factors
        self.scoring_weights = {
            "similarity": 0.3,
            "temporal": 0.2,
            "importance": 0.25,
            "context": 0.15,
            "emotional": 0.1
        }
        
        # Cache for recent searches
        self._search_cache: Dict[str, Tuple[List[RetrievalResult], datetime]] = {}
        self._cache_ttl = timedelta(minutes=5)
        
    async def search(
        self,
        query: str,
        memory_store,
        context: SearchContext,
        strategy: SearchStrategy = SearchStrategy.HYBRID_MULTI_MODAL,
        limit: int = 10,
        similarity_threshold: float = 0.1,
        diversity_factor: float = 0.3
    ) -> List[RetrievalResult]:
        """
        Perform intelligent memory search
        
        Args:
            query: Search query text
            context: Search context information
            strategy: Search strategy to use
            limit: Maximum number of results
            similarity_threshold: Minimum similarity threshold
            diversity_factor: Factor for result diversification (0.0-1.0)
            
        Returns:
            List of ranked retrieval results
        """
        try:
            # Check cache first
            cache_key = self._generate_cache_key(query, context, strategy)
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                return cached_result[:limit]
            
            # Determine memory types to search based on strategy and context
            memory_types = self._determine_search_scope(strategy, context)
            
            # Perform initial semantic search
            search_results = await memory_store.search_memories(
                query=query,
                memory_types=memory_types,
                limit=min(limit * 3, 50),  # Get more results for better ranking
                similarity_threshold=similarity_threshold
            )
            
            if not search_results:
                return []
            
            # Convert to retrieval results with detailed scoring
            retrieval_results = []
            for memory, similarity in search_results:
                result = await self._create_retrieval_result(
                    memory, similarity, query, context, strategy
                )
                retrieval_results.append(result)
            
            # Apply advanced ranking
            ranked_results = await self._rank_results(
                retrieval_results, query, context, strategy
            )
            
            # Apply diversity filtering if requested
            if diversity_factor > 0:
                ranked_results = await self._apply_diversity_filter(
                    ranked_results, diversity_factor
                )
            
            # Limit results
            final_results = ranked_results[:limit]
            
            # Cache the results
            self._cache_result(cache_key, ranked_results)
            
            logger.debug(f"Retrieved {len(final_results)} memories for query: {query}")
            
            return final_results
            
        except Exception as e:
            logger.error(f"Error in memory search: {e}")
            return []
    
    async def find_related(
        self,
        memory_id: str,
        memory_store,
        relationship_types: Optional[List[str]] = None,
        context: Optional[SearchContext] = None,
        limit: int = 5
    ) -> List[RetrievalResult]:
        """
        Find memories related to a specific memory
        
        Args:
            memory_id: ID of the source memory
            relationship_types: Types of relationships to consider
            context: Search context
            limit: Maximum number of results
            
        Returns:
            List of related memories
        """
        try:
            # Get the source memory  
            source_memory = await memory_store.retrieve_memory(memory_id)
            if not source_memory:
                return []
            
            # Use source memory content as query for finding related memories
            query = source_memory.content
            
            # Create search context if not provided
            if context is None:
                context = SearchContext(
                    user_id=source_memory.metadata.user_id,
                    session_id=source_memory.metadata.session_id
                )
            
            # Search for related memories
            results = await self.search(
                query=query,
                memory_store=memory_store,
                context=context,
                strategy=SearchStrategy.SEMANTIC_ONLY,
                limit=limit + 1,  # +1 because source memory might be included
                similarity_threshold=0.3
            )
            
            # Filter out the source memory itself
            related_results = [r for r in results if r.memory.memory_id != memory_id]
            
            return related_results[:limit]
            
        except Exception as e:
            logger.error(f"Error finding related memories: {e}")
            return []
    
    async def get_context_memories(
        self,
        context: SearchContext,
        limit: int = 5
    ) -> List[RetrievalResult]:
        """
        Get relevant memories based on current context
        
        Args:
            context: Current context information
            limit: Maximum number of results
            
        Returns:
            List of contextually relevant memories
        """
        try:
            # Build query from context
            query_parts = []
            
            if context.current_task:
                query_parts.append(context.current_task)
            
            if context.domain_focus:
                query_parts.append(context.domain_focus)
            
            if context.social_context:
                query_parts.extend(context.social_context)
            
            if not query_parts:
                # Fallback to recent memories
                return await self._get_recent_memories(context, limit)
            
            query = " ".join(query_parts)
            
            # Search with context-aware strategy
            results = await self.search(
                query=query,
                context=context,
                strategy=SearchStrategy.HYBRID_MULTI_MODAL,
                limit=limit,
                similarity_threshold=0.2
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting context memories: {e}")
            return []
    
    async def _create_retrieval_result(
        self,
        memory: BaseMemory,
        similarity_score: float,
        query: str,
        context: SearchContext,
        strategy: SearchStrategy
    ) -> RetrievalResult:
        """Create a detailed retrieval result with scoring"""
        try:
            # Calculate temporal score
            temporal_score = self._calculate_temporal_score(memory, context)
            
            # Get importance score
            importance_score = memory.metadata.importance_score
            
            # Calculate context score
            context_score = await self._calculate_context_score(memory, context)
            
            # Calculate final weighted score
            final_score = (
                self.scoring_weights["similarity"] * similarity_score +
                self.scoring_weights["temporal"] * temporal_score +
                self.scoring_weights["importance"] * importance_score +
                self.scoring_weights["context"] * context_score
            )
            
            # Generate explanation
            explanation = self._generate_explanation(
                similarity_score, temporal_score, importance_score, context_score
            )
            
            return RetrievalResult(
                memory=memory,
                relevance_score=final_score,
                similarity_score=similarity_score,
                temporal_score=temporal_score,
                importance_score=importance_score,
                context_score=context_score,
                final_score=final_score,
                explanation=explanation
            )
            
        except Exception as e:
            logger.error(f"Error creating retrieval result: {e}")
            # Return basic result
            return RetrievalResult(
                memory=memory,
                relevance_score=similarity_score,
                similarity_score=similarity_score,
                temporal_score=0.0,
                importance_score=memory.metadata.importance_score,
                context_score=0.0,
                final_score=similarity_score,
                explanation="Basic similarity match"
            )
    
    def _calculate_temporal_score(self, memory: BaseMemory, context: SearchContext) -> float:
        """Calculate temporal relevance score"""
        try:
            now = datetime.utcnow()
            memory_age = (now - memory.metadata.created_at).total_seconds()
            
            # Different decay rates for different memory types
            if memory.memory_type == MemoryType.WORKING:
                decay_rate = 0.001  # Fast decay for working memory
            elif memory.memory_type == MemoryType.SHORT_TERM:
                decay_rate = 0.0001  # Medium decay
            else:
                decay_rate = 0.00001  # Slow decay for long-term memories
            
            # Exponential decay with access frequency boost
            temporal_score = np.exp(-decay_rate * memory_age)
            
            # Boost based on access frequency
            access_boost = min(0.3, memory.metadata.access_count * 0.01)
            temporal_score += access_boost
            
            # Context-based temporal adjustments
            if context.time_context:
                time_diff = abs((context.time_context - memory.metadata.created_at).total_seconds())
                if time_diff < 3600:  # Within an hour
                    temporal_score += 0.2
                elif time_diff < 86400:  # Within a day
                    temporal_score += 0.1
            
            return min(1.0, temporal_score)
            
        except Exception as e:
            logger.error(f"Error calculating temporal score: {e}")
            return 0.5
    
    async def _calculate_context_score(self, memory: BaseMemory, context: SearchContext) -> float:
        """Calculate context relevance score"""
        try:
            score = 0.0
            
            # User context matching
            if context.user_id and memory.metadata.user_id == context.user_id:
                score += 0.3
            
            # Session context matching
            if context.session_id and memory.metadata.session_id == context.session_id:
                score += 0.2
            
            # Domain context matching
            if context.domain_focus:
                if hasattr(memory, 'domain') and memory.domain == context.domain_focus:
                    score += 0.3
                elif context.domain_focus.lower() in memory.content.lower():
                    score += 0.2
            
            # Social context matching
            if context.social_context and hasattr(memory, 'participants'):
                common_participants = set(context.social_context) & set(memory.participants)
                if common_participants:
                    score += 0.2 * (len(common_participants) / len(context.social_context))
            
            # Emotional context matching
            if context.emotional_state and hasattr(memory, 'emotional_state') and memory.emotional_state:
                emotional_similarity = self._calculate_emotional_similarity(
                    context.emotional_state, memory.emotional_state
                )
                score += 0.1 * emotional_similarity
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Error calculating context score: {e}")
            return 0.0
    
    def _calculate_emotional_similarity(self, emotion1: EmotionalState, emotion2: EmotionalState) -> float:
        """Calculate similarity between emotional states"""
        try:
            valence_diff = abs(emotion1.valence - emotion2.valence)
            arousal_diff = abs(emotion1.arousal - emotion2.arousal)
            dominance_diff = abs(emotion1.dominance - emotion2.dominance)
            
            # Average difference (lower is more similar)
            avg_diff = (valence_diff + arousal_diff + dominance_diff) / 3.0
            
            # Convert to similarity (0-1 scale)
            similarity = 1.0 - (avg_diff / 2.0)  # Max diff is 2.0
            
            return max(0.0, similarity)
            
        except Exception as e:
            logger.error(f"Error calculating emotional similarity: {e}")
            return 0.0
    
    async def _rank_results(
        self,
        results: List[RetrievalResult],
        query: str,
        context: SearchContext,
        strategy: SearchStrategy
    ) -> List[RetrievalResult]:
        """Apply advanced ranking to results"""
        try:
            # Sort by final score
            results.sort(key=lambda x: x.final_score, reverse=True)
            
            # Apply strategy-specific adjustments
            if strategy == SearchStrategy.TEMPORAL_WEIGHTED:
                # Boost recent memories
                for result in results:
                    result.final_score = (
                        0.4 * result.similarity_score +
                        0.6 * result.temporal_score
                    )
            
            elif strategy == SearchStrategy.EMOTIONAL_FILTERED:
                # Filter and boost emotionally relevant memories
                if context.emotional_state:
                    emotional_results = []
                    for result in results:
                        if hasattr(result.memory, 'emotional_state') and result.memory.emotional_state:
                            emotional_sim = self._calculate_emotional_similarity(
                                context.emotional_state, result.memory.emotional_state
                            )
                            if emotional_sim > 0.3:  # Threshold for emotional relevance
                                result.final_score += 0.2 * emotional_sim
                                emotional_results.append(result)
                    results = emotional_results
            
            # Re-sort after adjustments
            results.sort(key=lambda x: x.final_score, reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Error ranking results: {e}")
            return results
    
    async def _apply_diversity_filter(
        self, 
        results: List[RetrievalResult], 
        diversity_factor: float
    ) -> List[RetrievalResult]:
        """Apply diversity filtering to avoid too similar results"""
        try:
            if not results or diversity_factor <= 0:
                return results
            
            diverse_results = [results[0]]  # Always include the top result
            
            for result in results[1:]:
                # Check diversity against already selected results
                should_include = True
                
                for selected in diverse_results:
                    # Calculate content similarity
                    if result.memory.embedding and selected.memory.embedding:
                        similarity = self.llm_client.calculate_similarity(
                            result.memory.embedding, selected.memory.embedding
                        )
                        
                        # If too similar, skip based on diversity factor
                        if similarity > (1.0 - diversity_factor):
                            # Still include if significantly better score
                            score_diff = result.final_score - selected.final_score
                            if score_diff < 0.2:  # Not significantly better
                                should_include = False
                                break
                
                if should_include:
                    diverse_results.append(result)
            
            return diverse_results
            
        except Exception as e:
            logger.error(f"Error applying diversity filter: {e}")
            return results
    
    def _determine_search_scope(self, strategy: SearchStrategy, context: SearchContext) -> Optional[List[MemoryType]]:
        """Determine which memory types to search based on strategy and context"""
        if strategy == SearchStrategy.SOCIAL_CONTEXT:
            return [MemoryType.SOCIAL, MemoryType.EPISODIC]
        elif strategy == SearchStrategy.TEMPORAL_WEIGHTED:
            return [MemoryType.WORKING, MemoryType.SHORT_TERM, MemoryType.EPISODIC]
        elif context.current_task:
            return [MemoryType.PROCEDURAL, MemoryType.SEMANTIC, MemoryType.WORKING]
        else:
            return None  # Search all types
    
    def _generate_explanation(
        self, 
        similarity_score: float, 
        temporal_score: float, 
        importance_score: float, 
        context_score: float
    ) -> str:
        """Generate human-readable explanation for the retrieval result"""
        explanations = []
        
        if similarity_score > 0.8:
            explanations.append("high content similarity")
        elif similarity_score > 0.6:
            explanations.append("good content match")
        
        if temporal_score > 0.7:
            explanations.append("recent and frequently accessed")
        elif temporal_score > 0.4:
            explanations.append("moderately recent")
        
        if importance_score > 0.8:
            explanations.append("high importance")
        elif importance_score > 0.6:
            explanations.append("notable importance")
        
        if context_score > 0.5:
            explanations.append("strong contextual relevance")
        elif context_score > 0.3:
            explanations.append("some contextual relevance")
        
        if not explanations:
            explanations.append("basic similarity match")
        
        return ", ".join(explanations)
    
    async def _get_recent_memories(self, context: SearchContext, limit: int) -> List[RetrievalResult]:
        """Get recent memories as fallback"""
        try:
            # This is a simplified implementation
            # In practice, you'd query the memory store for recent memories
            return []
        except Exception as e:
            logger.error(f"Error getting recent memories: {e}")
            return []
    
    def _generate_cache_key(self, query: str, context: SearchContext, strategy: SearchStrategy) -> str:
        """Generate cache key for search results"""
        key_parts = [
            query,
            str(strategy),
            context.user_id or "none",
            context.session_id or "none",
            context.current_task or "none"
        ]
        return "|".join(key_parts)
    
    def _get_cached_result(self, cache_key: str) -> Optional[List[RetrievalResult]]:
        """Get cached search result if not expired"""
        if cache_key in self._search_cache:
            results, timestamp = self._search_cache[cache_key]
            if datetime.utcnow() - timestamp < self._cache_ttl:
                return results
            else:
                del self._search_cache[cache_key]
        return None
    
    def _cache_result(self, cache_key: str, results: List[RetrievalResult]):
        """Cache search results"""
        self._search_cache[cache_key] = (results, datetime.utcnow())
        
        # Clean old cache entries
        if len(self._search_cache) > 100:  # Max cache size
            oldest_key = min(self._search_cache.keys(), 
                           key=lambda k: self._search_cache[k][1])
            del self._search_cache[oldest_key] 