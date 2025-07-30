"""
Configuration management for NeuronMemory
"""

import os
from typing import Optional, Dict, Any
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables (still needed for NeuronMemoryConfig)
load_dotenv()

class AzureOpenAIConfig:
    """Azure OpenAI configuration"""
    def __init__(self):
        self.api_key = ""
        self.endpoint = ""
        self.api_version = ""
        self.deployment_name = "gpt-4o"
        self.embedding_deployment = "text-embedding-ada-002"
    
    def dict(self):
        """Return configuration as dictionary for compatibility"""
        return {
            "api_key": self.api_key,
            "endpoint": self.endpoint,
            "api_version": self.api_version,
            "deployment_name": self.deployment_name,
            "embedding_deployment": self.embedding_deployment
        }

class NeuronMemoryConfig(BaseSettings):
    """NeuronMemory core configuration"""
    log_level: str = Field("INFO", env="NEURON_MEMORY_LOG_LEVEL")
    max_memory_size: int = Field(100000, env="NEURON_MEMORY_MAX_MEMORY_SIZE")
    embedding_model: str = Field("text-embedding-ada-002", env="NEURON_MEMORY_EMBEDDING_MODEL")
    vector_store: str = Field("chromadb", env="NEURON_MEMORY_VECTOR_STORE")
    
    # Database paths
    chroma_db_path: str = Field("./data/chromadb", env="CHROMA_DB_PATH")
    memory_store_path: str = Field("./data/memory_store", env="MEMORY_STORE_PATH")
    
    # Performance settings
    max_concurrent_operations: int = Field(10, env="MAX_CONCURRENT_OPERATIONS")
    memory_consolidation_interval: int = Field(3600, env="MEMORY_CONSOLIDATION_INTERVAL")
    cleanup_interval: int = Field(86400, env="CLEANUP_INTERVAL")
    
    # Memory parameters
    working_memory_capacity: int = Field(8000, description="Working memory token capacity")
    short_term_memory_duration: int = Field(259200, description="Short-term memory duration in seconds (72 hours)")
    importance_threshold: float = Field(0.1, description="Minimum importance score for memory storage")
    similarity_threshold: float = Field(0.7, description="Similarity threshold for memory deduplication")
    
    class Config:
        env_file = ".env"

# Global configuration instances
azure_openai_config = AzureOpenAIConfig()
neuron_memory_config = NeuronMemoryConfig()

def get_config() -> Dict[str, Any]:
    """Get all configuration as a dictionary"""
    return {
        "azure_openai": azure_openai_config.dict(),
        "neuron_memory": neuron_memory_config.dict(),
    }

def validate_config() -> bool:
    """Validate that all required configuration is present"""
    try:
        # Check Azure OpenAI config
        if not azure_openai_config.api_key:
            raise ValueError("azure_openai_api_key is required")
        if not azure_openai_config.endpoint:
            raise ValueError("azure_openai_endpoint is required")
        
        # Create data directories if they don't exist
        os.makedirs(neuron_memory_config.chroma_db_path, exist_ok=True)
        os.makedirs(neuron_memory_config.memory_store_path, exist_ok=True)
        
        return True
    except Exception as e:
        print(f"Configuration validation failed: {e}")
        return False 