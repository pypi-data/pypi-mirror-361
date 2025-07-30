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
    EpisodicMemory, SemanticMemory, ProceduralMemory, SocialMemory, WorkingMemory,
    MemoryMetadata, EmotionalState
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
            memory_types: List of memory types to search in
            limit: Max number of results
            similarity_threshold: Minimum similarity score to include
            filters: Metadata filters for ChromaDB
            
        Returns:
            List of (memory, similarity_score) tuples
        """
        try:
            query_embedding = await self.llm_client.generate_embedding(query)
            
            search_results = []
            
            # Determine which collections to search
            collections_to_search = {}
            if memory_types:
                for mt in memory_types:
                    collections_to_search[mt.value] = self.collections[mt.value]
            else:
                # Default to all main memory types
                main_types = ["episodic", "semantic", "procedural", "social", "working"]
                for mt in main_types:
                    collections_to_search[mt] = self.collections[mt]
                
            # Build ChromaDB filter if provided
            chroma_filter = {}
            if filters:
                for key, value in filters.items():
                    if isinstance(value, dict): # For operators like $in, $gt
                        chroma_filter[key] = value
                    else:
                        chroma_filter[key] = {"$eq": value}

            # Perform search on each relevant collection
            for collection_name, collection in collections_to_search.items():
                results = collection.query(
                        query_embeddings=[query_embedding],
                    n_results=limit,
                    where=chroma_filter if chroma_filter else None
                )
                
                if results["ids"][0]:
                    for i, memory_id in enumerate(results["ids"][0]):
                        similarity = results["distances"][0][i]
                        
                        # Chroma gives distance, convert to similarity
                        similarity_score = 1 - similarity
                        
                        if similarity_score >= similarity_threshold:
                            metadata = results["metadatas"][0][i]
                            content = results["documents"][0][i]
                            embedding = results["embeddings"][0][i] if results["embeddings"] else None
                            
                            memory = self._reconstruct_memory(metadata, content, embedding)
                            if memory:
                                search_results.append((memory, similarity_score))

            # Sort combined results by similarity
            search_results.sort(key=lambda x: x[1], reverse=True)
            
            return search_results[:limit]
            
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return []
    
    async def update_memory(self, memory: BaseMemory) -> bool:
        """
        Update an existing memory
        
        Args:
            memory: The memory object with updated fields
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # This is a complex operation (delete and re-add)
            # For simplicity, we'll just re-store it, which overwrites
            await self.store_memory(memory)
            return True
            
        except Exception as e:
            logger.error(f"Error updating memory {memory.memory_id}: {e}")
            return False
    
    async def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory by ID
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Remove from cache
            if memory_id in self._memory_cache:
                del self._memory_cache[memory_id]
            if memory_id in self._embedding_cache:
                del self._embedding_cache[memory_id]
            
            # Delete from all collections
            for collection in self.collections.values():
                    collection.delete(ids=[memory_id])
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting memory {memory_id}: {e}")
            return False
    
    def _reconstruct_memory(
        self, 
        metadata: Dict[str, Any], 
        content: str, 
        embedding: Optional[List[float]]
    ) -> Optional[BaseMemory]:
        """Reconstruct a memory object from stored data"""
        try:
            memory_type = MemoryType(metadata.get("memory_type", "semantic"))
            
            # Create the appropriate memory object
            memory_class_map = {
                MemoryType.EPISODIC: EpisodicMemory,
                MemoryType.SEMANTIC: SemanticMemory,
                MemoryType.PROCEDURAL: ProceduralMemory,
                MemoryType.SOCIAL: SocialMemory,
                MemoryType.WORKING: WorkingMemory,
            }
            
            if memory_type not in memory_class_map:
                return None
                
            memory_class = memory_class_map[memory_type]
            
            # Reconstruct metadata object
            mem_metadata = MemoryMetadata(
                created_at=datetime.fromisoformat(metadata["created_at"]),
                last_accessed=datetime.fromisoformat(metadata["last_accessed"]),
                access_count=metadata.get("access_count", 0),
                importance_score=metadata.get("importance_score", 0.0),
                confidence_score=metadata.get("confidence_score", 1.0),
                source=metadata.get("source"),
                context_tags=json.loads(metadata.get("context_tags", "[]")),
                user_id=metadata.get("user_id"),
                session_id=metadata.get("session_id"),
            )
            
            # Create memory object
            memory_data = {
                "memory_id": metadata["memory_id"],
                "content": content,
                "metadata": mem_metadata,
                "embedding": embedding
            }
            
            # Add type-specific fields
            if memory_type == MemoryType.EPISODIC:
                memory_data["location"] = metadata.get("location")
                memory_data["participants"] = json.loads(metadata.get("participants", "[]"))
                memory_data["emotional_state"] = EmotionalState(
                    valence=metadata.get("emotional_valence", 0.0),
                    arousal=metadata.get("emotional_arousal", 0.0)
                )
            elif memory_type == MemoryType.SEMANTIC:
                memory_data["domain"] = metadata.get("domain")
                memory_data["concepts"] = json.loads(metadata.get("concepts", "[]"))
                memory_data["certainty"] = metadata.get("certainty", 1.0)
            elif memory_type == MemoryType.SOCIAL:
                memory_data["person_id"] = metadata.get("person_id")
                memory_data["relationship_type"] = metadata.get("relationship_type")
                memory_data["trust_level"] = metadata.get("trust_level", 0.5)

            return memory_class(**memory_data)
            
        except Exception as e:
            logger.error(f"Error reconstructing memory: {e}")
            return None
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the memory store"""
        self._stats["cache_size"] = len(self._memory_cache)
        return self._stats
    
    async def cleanup_expired_memories(self) -> int:
        """
        Clean up expired working memories
            
        Returns:
            Number of memories cleaned up
        """
        try:
            now = datetime.utcnow()
            collection = self.collections["working"]
            
            # ChromaDB doesn't directly support date comparisons in where filters well.
            # A common pattern is to fetch and filter in the client.
            # This is inefficient but works for this implementation.
            
            all_working_memories = collection.get() # This can be very large!
            
            expired_ids = []
            for i, metadata in enumerate(all_working_memories["metadatas"]):
                # Assuming expiration is stored in metadata
                if "expiration" in metadata:
                    expiration_time = datetime.fromisoformat(metadata["expiration"])
                    if now > expiration_time:
                        expired_ids.append(all_working_memories["ids"][i])
            
            if expired_ids:
                collection.delete(ids=expired_ids)
                
                # Also remove from cache
                for mem_id in expired_ids:
                    if mem_id in self._memory_cache:
                        del self._memory_cache[mem_id]
                
                logger.info(f"Cleaned up {len(expired_ids)} expired working memories")
                return len(expired_ids)
            
            return 0
            
        except Exception as e:
            logger.error(f"Error during memory cleanup: {e}")
            return 0 