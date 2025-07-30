"""
Core Retrieval Engine for NeuronMemory

This module provides the advanced retrieval logic, including:
- Multi-faceted scoring (semantic, temporal, contextual)
- Search strategy handling
- Result ranking and diversification
- Caching for performance
"""

import asyncio
import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from ..llm.azure_openai_client import AzureOpenAIClient
from ..memory.memory_objects import BaseMemory, EmotionalState

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
    Handles complex memory retrieval and ranking logic.
    """

    def __init__(self):
        """Initialize the retrieval engine"""
        self.llm_client = AzureOpenAIClient()
        self.result_cache: Dict[str, List[RetrievalResult]] = {}
        self.cache_ttl = timedelta(minutes=5)

        # Scoring weights (tunable)
        self.scoring_weights = {
            "similarity": 0.5,
            "temporal": 0.2,
            "importance": 0.15,
            "context": 0.1,
            "emotional": 0.05,
        }

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
        Main search entry point.

        Orchestrates the search, scoring, ranking, and filtering process.
        """
        try:
            # Check cache first
            cache_key = self._generate_cache_key(query, context, strategy)
            cached_results = self._get_cached_result(cache_key)
            if cached_results:
                logger.debug(f"Returning cached results for query: {query}")
                return cached_results

            # Determine search parameters based on strategy
            filters = {}
            if strategy == SearchStrategy.SOCIAL_CONTEXT and context.user_id:
                filters["user_id"] = context.user_id

            # Initial semantic search
            semantic_results = await memory_store.search_memories(
                query=query,
                limit=limit * 3,  # Fetch more to allow for re-ranking
                similarity_threshold=similarity_threshold,
                filters=filters
            )

            if not semantic_results:
                return []

            # Create detailed retrieval results with advanced scoring
            retrieval_results = []
            for memory, similarity_score in semantic_results:
                result = await self._create_retrieval_result(
                    memory, similarity_score, query, context, strategy
                )
                retrieval_results.append(result)

            # Re-rank results
            ranked_results = await self._rank_results(
                retrieval_results, query, context, strategy
            )

            # Apply diversity filter
            if diversity_factor > 0:
                final_results = await self._apply_diversity_filter(
                    ranked_results, diversity_factor
                )
            else:
                final_results = ranked_results

            # Limit and cache the final results
            final_results = final_results[:limit]
            self._cache_result(cache_key, final_results)

            return final_results

        except Exception as e:
            logger.error(f"Error during search: {e}", exc_info=True)
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
        Find memories related to a given memory.
        (Future implementation)
        """
        # This is a placeholder for a more advanced relationship traversal
        # For now, it could do a semantic search using the content of the
        # source memory.
        source_memory = await memory_store.retrieve_memory(memory_id)
        if not source_memory:
            return []

        if not context:
            context = SearchContext()

        return await self.search(
            query=source_memory.content,
            memory_store=memory_store,
            context=context,
            limit=limit,
        )

    async def get_context_memories(
        self,
        context: SearchContext,
        limit: int = 5
    ) -> List[RetrievalResult]:
        """
        Retrieve memories based on the current context without a specific query.
        (Future implementation)
        """
        # This could involve finding recent memories, memories related to the
        # current user/task, etc.
        try:
            # For now, let's use the current task as a query
            if context.current_task:
                return await self.search(
                    query=context.current_task,
                    memory_store=self,  # Needs a MemoryStore instance
                    context=context,
                    limit=limit
                )
            return []
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
        """Create a detailed retrieval result object with all scores"""
        # Temporal scoring
        temporal_score = self._calculate_temporal_score(memory, context)

        # Importance scoring
        importance_score = memory.metadata.importance_score

        # Contextual scoring
        context_score = await self._calculate_context_score(memory, context)

        # Emotional scoring (if applicable)
        emotional_score = 0.0
        if strategy == SearchStrategy.EMOTIONAL_FILTERED and context.emotional_state and hasattr(memory, 'emotional_state') and memory.emotional_state:
            emotional_score = self._calculate_emotional_similarity(
                context.emotional_state, memory.emotional_state
            )

        # Final weighted score
        final_score = (
            similarity_score * self.scoring_weights["similarity"] +
            temporal_score * self.scoring_weights["temporal"] +
            importance_score * self.scoring_weights["importance"] +
            context_score * self.scoring_weights["context"] +
            emotional_score * self.scoring_weights["emotional"]
        )

        # Generate explanation
        explanation = self._generate_explanation(
            similarity_score, temporal_score, importance_score, context_score
        )

        return RetrievalResult(
            memory=memory,
            relevance_score=final_score,  # Using final_score as relevance for MMR
            similarity_score=similarity_score,
            temporal_score=temporal_score,
            importance_score=importance_score,
            context_score=context_score,
            final_score=final_score,
            explanation=explanation
        )

    def _calculate_temporal_score(self, memory: BaseMemory, context: SearchContext) -> float:
        """
        Calculate a temporal relevance score (0.0 to 1.0)
        Recency is key, but access patterns also matter.
        """
        now = context.time_context or datetime.utcnow()
        last_access_hours = (now - memory.metadata.last_accessed).total_seconds() / 3600

        # Sigmoid function for smooth decay
        score = 1 / (1 + (last_access_hours / 24)**2)

        # Boost for frequently accessed memories
        access_boost = min(0.2, (memory.metadata.access_count / 100))

        return min(1.0, score + access_boost)

    async def _calculate_context_score(self, memory: BaseMemory, context: SearchContext) -> float:
        """
        Calculate a contextual relevance score based on tags, domain, user, etc.
        """
        score = 0.0

        if context.user_id and memory.metadata.user_id == context.user_id:
            score += 0.4

        if context.session_id and memory.metadata.session_id == context.session_id:
            score += 0.4

        if context.current_task or context.domain_focus:
            context_text = f"{context.current_task or ''} {context.domain_focus or ''}"
            if memory.metadata.context_tags:
                relevance_check = await self.llm_client.compare_relevance(
                    text1=context_text,
                    text2=" ".join(memory.metadata.context_tags)
                )
                score += 0.2 * relevance_check

        return min(1.0, score)

    def _calculate_emotional_similarity(self, emotion1: EmotionalState, emotion2: EmotionalState) -> float:
        """
        Calculate emotional similarity using cosine similarity on VAD space
        """
        v1 = np.array([emotion1.valence, emotion1.arousal])
        v2 = np.array([emotion2.valence, emotion2.arousal])

        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)

        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0

        return np.dot(v1, v2) / (norm_v1 * norm_v2)

    async def _rank_results(
        self,
        results: List[RetrievalResult],
        query: str,
        context: SearchContext,
        strategy: SearchStrategy
    ) -> List[RetrievalResult]:
        """
        Re-rank results using the calculated final_score.
        """
        results.sort(key=lambda r: r.final_score, reverse=True)
        return results

    async def _apply_diversity_filter(
        self,
        results: List[RetrievalResult],
        diversity_factor: float
    ) -> List[RetrievalResult]:
        """
        Apply Maximal Marginal Relevance (MMR) for diversity.
        """
        if not results or not all(r.memory.embedding is not None for r in results):
            return results

        lambda_param = max(0.0, min(1.0, diversity_factor))
        if lambda_param == 0:
            return results
        
        selected_results: List[RetrievalResult] = []
        remaining_results = results[:]

        if remaining_results:
            selected_results.append(remaining_results.pop(0))

        while remaining_results:
            best_next_result = None
            max_mmr_score = -np.inf

            for result in remaining_results:
                similarity_to_selected = max(
                    [
                        np.dot(result.memory.embedding, sel.memory.embedding)
                        for sel in selected_results if sel.memory.embedding is not None
                    ]
                ) if selected_results else 0.0

                mmr_score = (
                    lambda_param * result.relevance_score -
                    (1 - lambda_param) * similarity_to_selected
                )

                if mmr_score > max_mmr_score:
                    max_mmr_score = mmr_score
                    best_next_result = result

            if best_next_result:
                selected_results.append(best_next_result)
                remaining_results.remove(best_next_result)
            else:
                break

        return selected_results

    def _generate_explanation(
        self,
        similarity_score: float,
        temporal_score: float,
        importance_score: float,
        context_score: float
    ) -> str:
        """Generate a human-readable explanation of the score."""
        return (
            f"Retrieved due to a combination of factors: "
            f"semantic similarity ({similarity_score:.2f}), "
            f"temporal relevance ({temporal_score:.2f}), "
            f"inherent importance ({importance_score:.2f}), "
            f"and contextual match ({context_score:.2f})."
        )

    def _generate_cache_key(self, query: str, context: SearchContext, strategy: SearchStrategy) -> str:
        """Generate a consistent cache key for a search request."""
        context_str = json.dumps(context.__dict__, sort_keys=True, default=str)
        key_str = f"{query}:{context_str}:{strategy.value}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def _get_cached_result(self, cache_key: str) -> Optional[List[RetrievalResult]]:
        """Get result from cache if not expired."""
        if cache_key in self.result_cache:
            # A more robust implementation would check TTL
            return self.result_cache[cache_key]
        return None

    def _cache_result(self, cache_key: str, results: List[RetrievalResult]):
        """Cache a search result."""
        self.result_cache[cache_key] = results 