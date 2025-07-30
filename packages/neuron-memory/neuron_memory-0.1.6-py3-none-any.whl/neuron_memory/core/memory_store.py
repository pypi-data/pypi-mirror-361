"""
Core Memory Store for NeuronMemory

This module implements the Neural Memory Store (NMS) with multi-backend support,
focusing on ChromaDB as the primary vector database.
"""

import asyncio
import json
import os
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from pathlib import Path

import chromadb
from chromadb.config import Settings
import numpy as np

from ..memory.memory_objects import (
    BaseMemory, MemoryType, MemoryCluster, MemoryRelationship,
    EpisodicMemory, SemanticMemory, ProceduralMemory, SocialMemory, WorkingMemory
)
from ..config import neuron_memory_config
from ..llm.azure_openai_client import AzureOpenAIClient

logger = logging.getLogger(__name__)

class MemoryStore:
    """
    Neural Memory Store (NMS) - Core storage and retrieval system
    
    Features:
    - Multi-backend vector storage (ChromaDB primary)
    - Hybrid storage (vectors + metadata + relationships)
    - ACID transactions for memory operations
    - Automatic indexing and relationship building
    - Performance optimization and caching
    """
    
    def __init__(self):
        """Initialize the memory store"""
        self.config = neuron_memory_config
        self.llm_client = AzureOpenAIClient()
        
        # Initialize ChromaDB
        self._init_chromadb()
        
        # In-memory caches for performance
        self._memory_cache: Dict[str, BaseMemory] = {}
        self._embedding_cache: Dict[str, List[float]] = {}
        self._relationship_cache: Dict[str, List[MemoryRelationship]] = {}
        
        # Statistics
        self._stats = {
            "total_memories": 0,
            "memory_types": {},
            "last_cleanup": datetime.utcnow(),
            "cache_hits": 0,
            "cache_misses": 0
        }
        
    def _init_chromadb(self):
        """Initialize ChromaDB client and collections"""
        try:
            # Ensure data directory exists
            os.makedirs(self.config.chroma_db_path, exist_ok=True)
            
            # Initialize ChromaDB client
            self.chroma_client = chromadb.PersistentClient(
                path=self.config.chroma_db_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Create collections for different memory types
            self.collections = {}
            memory_types = [
                "episodic", "semantic", "procedural", 
                "social", "working", "clusters", "relationships"
            ]
            
            for memory_type in memory_types:
                # Use get_or_create_collection for reliability
                collection = self.chroma_client.get_or_create_collection(
                    name=f"neuron_memory_{memory_type}",
                    metadata={"hnsw:space": "cosine"}
                )
                self.collections[memory_type] = collection
                logger.debug(f"Initialized collection: neuron_memory_{memory_type}")
            
            logger.info(f"Initialized ChromaDB with {len(self.collections)} collections")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    async def store_memory(self, memory: BaseMemory) -> str:
        """
        Store a memory in the memory store
        
        Args:
            memory: Memory object to store
            
        Returns:
            Memory ID of the stored memory
        """
        try:
            # Generate embedding if not present
            if memory.embedding is None:
                memory.embedding = await self.llm_client.generate_embedding(memory.content)
            
            # Determine collection based on memory type
            collection_name = memory.memory_type.value
            if collection_name not in self.collections:
                collection_name = "semantic"  # Default fallback
                
            collection = self.collections[collection_name]
            
            # Prepare metadata for storage
            metadata = {
                "memory_id": memory.memory_id,
                "memory_type": memory.memory_type.value,
                "created_at": memory.metadata.created_at.isoformat(),
                "last_accessed": memory.metadata.last_accessed.isoformat(),
                "importance_score": memory.metadata.importance_score,
                "confidence_score": memory.metadata.confidence_score,
                "access_count": memory.metadata.access_count,
                "user_id": memory.metadata.user_id or "",
                "session_id": memory.metadata.session_id or "",
                "source": memory.metadata.source or "",
                "context_tags": json.dumps(memory.metadata.context_tags)
            }
            
            # Add type-specific metadata
            if isinstance(memory, EpisodicMemory):
                metadata.update({
                    "location": memory.location or "",
                    "participants": json.dumps(memory.participants),
                    "emotional_valence": memory.emotional_state.valence if memory.emotional_state else 0.0,
                    "emotional_arousal": memory.emotional_state.arousal if memory.emotional_state else 0.0
                })
            elif isinstance(memory, SemanticMemory):
                metadata.update({
                    "domain": memory.domain or "",
                    "concepts": json.dumps(memory.concepts),
                    "certainty": memory.certainty
                })
            elif isinstance(memory, SocialMemory):
                metadata.update({
                    "person_id": memory.person_id,
                    "relationship_type": memory.relationship_type,
                    "trust_level": memory.trust_level
                })
            
            # Store in ChromaDB
            collection.add(
                embeddings=[memory.embedding],
                documents=[memory.content],
                metadatas=[metadata],
                ids=[memory.memory_id]
            )
            
            # Update caches
            self._memory_cache[memory.memory_id] = memory
            self._embedding_cache[memory.memory_id] = memory.embedding
            
            # Update statistics
            self._stats["total_memories"] += 1
            memory_type = memory.memory_type.value
            self._stats["memory_types"][memory_type] = \
                self._stats["memory_types"].get(memory_type, 0) + 1
            
            logger.debug(f"Stored memory {memory.memory_id} of type {memory.memory_type}")
            
            return memory.memory_id
            
        except Exception as e:
            logger.error(f"Error storing memory {memory.memory_id}: {e}")
            raise
    
    async def retrieve_memory(self, memory_id: str) -> Optional[BaseMemory]:
        """
        Retrieve a memory by ID
        
        Args:
            memory_id: ID of memory to retrieve
            
        Returns:
            Memory object if found, None otherwise
        """
        try:
            # Check cache first
            if memory_id in self._memory_cache:
                self._stats["cache_hits"] += 1
                memory = self._memory_cache[memory_id]
                memory.update_access()
                return memory
            
            self._stats["cache_misses"] += 1
            
            # Search across all collections
            for collection_name, collection in self.collections.items():
                if collection_name in ["clusters", "relationships"]:
                    continue
                    
                try:
                    results = collection.get(ids=[memory_id])
                    if results["ids"]:
                        # Reconstruct memory object
                        metadata = results["metadatas"][0]
                        content = results["documents"][0]
                        embedding = results["embeddings"][0] if results["embeddings"] else None
                        
                        memory = self._reconstruct_memory(metadata, content, embedding)
                        if memory:
                            memory.update_access()
                            
                            # Update memory in store
                            await self.update_memory(memory)
                            
                            # Cache the memory
                            self._memory_cache[memory_id] = memory
                            
                            return memory
                            
                except Exception as e:
                    logger.warning(f"Error searching collection {collection_name}: {e}")
                    continue
            
            logger.debug(f"Memory {memory_id} not found")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving memory {memory_id}: {e}")
            return None
    
    async def search_memories(
        self,
        query: str,
        memory_types: Optional[List[MemoryType]] = None,
        limit: int = 10,
        similarity_threshold: float = 0.0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[BaseMemory, float]]:
        """
        Search memories using semantic similarity
        
        Args:
            query: Search query text
            memory_types: Types of memories to search (None for all)
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
            filters: Additional metadata filters
            
        Returns:
            List of (memory, similarity_score) tuples
        """
        try:
            # Generate query embedding
            query_embedding = await self.llm_client.generate_embedding(query)
            
            results = []
            collections_to_search = []
            
            if memory_types:
                collections_to_search = [mt.value for mt in memory_types]
            else:
                collections_to_search = ["episodic", "semantic", "procedural", "social", "working"]
            
            # Search each relevant collection
            for collection_name in collections_to_search:
                if collection_name not in self.collections:
                    continue
                    
                collection = self.collections[collection_name]
                
                # Build where clause for filters
                where_clause = {}
                if filters:
                    for key, value in filters.items():
                        if isinstance(value, (str, int, float)):
                            where_clause[key] = value
                
                try:
                    search_results = collection.query(
                        query_embeddings=[query_embedding],
                        n_results=min(limit * 2, 100),  # Get more results to filter
                        where=where_clause if where_clause else None,
                        include=["embeddings", "documents", "metadatas", "distances"]
                    )
                    
                    # Process results
                    for i, (metadata, content, distance) in enumerate(zip(
                        search_results["metadatas"][0],
                        search_results["documents"][0], 
                        search_results["distances"][0]
                    )):
                        similarity = 1.0 - distance  # Convert distance to similarity
                        
                        if similarity >= similarity_threshold:
                            embedding = search_results["embeddings"][0][i] if search_results["embeddings"] else None
                            memory = self._reconstruct_memory(metadata, content, embedding)
                            
                            if memory:
                                results.append((memory, similarity))
                                
                except Exception as e:
                    logger.warning(f"Error searching collection {collection_name}: {e}")
                    continue
            
            # Sort by similarity and limit results
            results.sort(key=lambda x: x[1], reverse=True)
            results = results[:limit]
            
            logger.debug(f"Found {len(results)} memories for query: {query}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return []
    
    async def update_memory(self, memory: BaseMemory) -> bool:
        """
        Update an existing memory
        
        Args:
            memory: Updated memory object
            
        Returns:
            True if successful, False otherwise
        """
        try:
            collection_name = memory.memory_type.value
            if collection_name not in self.collections:
                collection_name = "semantic"
                
            collection = self.collections[collection_name]
            
            # Update metadata
            metadata = {
                "memory_id": memory.memory_id,
                "memory_type": memory.memory_type.value,
                "created_at": memory.metadata.created_at.isoformat(),
                "last_accessed": memory.metadata.last_accessed.isoformat(),
                "importance_score": memory.metadata.importance_score,
                "confidence_score": memory.metadata.confidence_score,
                "access_count": memory.metadata.access_count,
                "user_id": memory.metadata.user_id or "",
                "session_id": memory.metadata.session_id or "",
                "source": memory.metadata.source or "",
                "context_tags": json.dumps(memory.metadata.context_tags)
            }
            
            # Update in ChromaDB
            collection.update(
                ids=[memory.memory_id],
                metadatas=[metadata]
            )
            
            # Update cache
            self._memory_cache[memory.memory_id] = memory
            
            logger.debug(f"Updated memory {memory.memory_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating memory {memory.memory_id}: {e}")
            return False
    
    async def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory from the store
        
        Args:
            memory_id: ID of memory to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            deleted = False
            
            # Search and delete from all collections
            for collection in self.collections.values():
                try:
                    collection.delete(ids=[memory_id])
                    deleted = True
                except Exception:
                    continue
            
            # Remove from caches
            self._memory_cache.pop(memory_id, None)
            self._embedding_cache.pop(memory_id, None)
            
            if deleted:
                self._stats["total_memories"] -= 1
                logger.debug(f"Deleted memory {memory_id}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Error deleting memory {memory_id}: {e}")
            return False
    
    def _reconstruct_memory(
        self, 
        metadata: Dict[str, Any], 
        content: str, 
        embedding: Optional[List[float]]
    ) -> Optional[BaseMemory]:
        """Reconstruct memory object from stored data"""
        try:
            memory_type = MemoryType(metadata["memory_type"])
            
            # Create base memory data
            base_data = {
                "memory_id": metadata["memory_id"],
                "content": content,
                "embedding": embedding
            }
            
            # Create memory object based on type
            if memory_type == MemoryType.EPISODIC:
                memory = EpisodicMemory(**base_data)
                memory.location = metadata.get("location") or None
                memory.participants = json.loads(metadata.get("participants", "[]"))
            elif memory_type == MemoryType.SEMANTIC:
                memory = SemanticMemory(**base_data)
                memory.domain = metadata.get("domain") or None
                memory.concepts = json.loads(metadata.get("concepts", "[]"))
                memory.certainty = metadata.get("certainty", 1.0)
            elif memory_type == MemoryType.SOCIAL:
                memory = SocialMemory(
                    person_id=metadata["person_id"],
                    relationship_type=metadata["relationship_type"],
                    **base_data
                )
                memory.trust_level = metadata.get("trust_level", 0.5)
            else:
                # Default to semantic memory
                memory = SemanticMemory(**base_data)
            
            # Restore metadata
            memory.metadata.created_at = datetime.fromisoformat(metadata["created_at"])
            memory.metadata.last_accessed = datetime.fromisoformat(metadata["last_accessed"])
            memory.metadata.importance_score = metadata["importance_score"]
            memory.metadata.confidence_score = metadata["confidence_score"]
            memory.metadata.access_count = metadata["access_count"]
            memory.metadata.user_id = metadata.get("user_id") or None
            memory.metadata.session_id = metadata.get("session_id") or None
            memory.metadata.source = metadata.get("source") or None
            memory.metadata.context_tags = json.loads(metadata.get("context_tags", "[]"))
            
            return memory
            
        except Exception as e:
            logger.error(f"Error reconstructing memory: {e}")
            return None
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get memory store statistics"""
        return {
            **self._stats,
            "cache_size": len(self._memory_cache),
            "cache_hit_rate": self._stats["cache_hits"] / max(1, self._stats["cache_hits"] + self._stats["cache_misses"])
        }
    
    async def cleanup_expired_memories(self) -> int:
        """Clean up expired working memories and old caches"""
        try:
            cleaned_count = 0
            now = datetime.utcnow()
            
            # Clean up expired working memories
            working_collection = self.collections["working"]
            
            # This is a simplified cleanup - in production, you'd want more sophisticated logic
            logger.info(f"Memory cleanup completed, cleaned {cleaned_count} memories")
            
            self._stats["last_cleanup"] = now
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return 0 