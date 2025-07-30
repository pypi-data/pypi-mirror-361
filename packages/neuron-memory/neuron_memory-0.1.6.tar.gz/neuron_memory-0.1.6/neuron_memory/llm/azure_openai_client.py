"""
Azure OpenAI client for NeuronMemory

This module provides integration with Azure OpenAI services for embeddings
and LLM interactions within the NeuronMemory system.
"""

import asyncio
from typing import List, Dict, Any, Optional, Union
import numpy as np
from openai import AzureOpenAI
import logging
from ..config import azure_openai_config

logger = logging.getLogger(__name__)

class AzureOpenAIClient:
    """Azure OpenAI client for embeddings and chat completions"""
    
    def __init__(self):
        """Initialize the Azure OpenAI client"""
        self.client = AzureOpenAI(
            api_key=azure_openai_config.api_key,
            api_version=azure_openai_config.api_version,
            azure_endpoint=azure_openai_config.endpoint
        )
        self.embedding_deployment = azure_openai_config.embedding_deployment
        self.chat_deployment = azure_openai_config.deployment_name
        
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a text"""
        try:
            # Remove newlines and excessive whitespace
            text = " ".join(text.split())
            
            response = self.client.embeddings.create(
                input=text,
                model=self.embedding_deployment
            )
            
            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding for text of length {len(text)}")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts in batch"""
        try:
            # Clean texts
            cleaned_texts = [" ".join(text.split()) for text in texts]
            
            response = self.client.embeddings.create(
                input=cleaned_texts,
                model=self.embedding_deployment
            )
            
            embeddings = [data.embedding for data in response.data]
            logger.debug(f"Generated {len(embeddings)} embeddings in batch")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """Generate chat completion"""
        try:
            response = self.client.chat.completions.create(
                model=self.chat_deployment,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            content = response.choices[0].message.content
            logger.debug(f"Generated chat completion with {len(content)} characters")
            
            return content
            
        except Exception as e:
            logger.error(f"Error generating chat completion: {e}")
            raise
    
    async def analyze_importance(self, content: str, context: str = "") -> float:
        """Analyze the importance of content for memory storage"""
        try:
            prompt = f"""
            Analyze the importance of the following content for long-term memory storage.
            Rate from 0.0 to 1.0 where:
            - 0.0-0.2: Trivial, temporary information
            - 0.2-0.4: Somewhat useful information
            - 0.4-0.6: Moderately important information
            - 0.6-0.8: Important information worth remembering
            - 0.8-1.0: Critical information that must be remembered
            
            Context: {context}
            Content: {content}
            
            Respond with only a number between 0.0 and 1.0:
            """
            
            messages = [{"role": "user", "content": prompt}]
            response = await self.chat_completion(messages, temperature=0.1, max_tokens=10)
            
            try:
                importance = float(response.strip())
                return max(0.0, min(1.0, importance))  # Clamp to valid range
            except ValueError:
                logger.warning(f"Could not parse importance score: {response}")
                return 0.5  # Default moderate importance
                
        except Exception as e:
            logger.error(f"Error analyzing importance: {e}")
            return 0.5
    
    async def extract_entities(self, content: str) -> List[str]:
        """Extract named entities from content"""
        try:
            prompt = f"""
            Extract the key entities (people, places, organizations, concepts) from the following text.
            Return ONLY a valid JSON array of strings, nothing else.
            
            Text: {content}
            """
            
            messages = [{"role": "user", "content": prompt}]
            response = await self.chat_completion(messages, temperature=0.1, max_tokens=200)
            
            try:
                import json
                import re
                
                # Extract JSON from markdown code blocks or find JSON array
                json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # Try to find JSON array in the response
                    json_match = re.search(r'\[.*?\]', response, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                    else:
                        json_str = response.strip()
                
                entities = json.loads(json_str)
                return entities if isinstance(entities, list) else []
            except (json.JSONDecodeError, ValueError, AttributeError):
                logger.warning(f"Could not parse entities: {response}")
                return []
                
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return []
    
    async def detect_emotion(self, content: str) -> Dict[str, float]:
        """Detect emotional content in text"""
        try:
            prompt = f"""
            Analyze the emotional content of the following text.
            Return ONLY a valid JSON object with valence, arousal, and dominance values between -1.0 and 1.0.
            
            Text: {content}
            """
            
            messages = [{"role": "user", "content": prompt}]
            response = await self.chat_completion(messages, temperature=0.1, max_tokens=100)
            
            try:
                import json
                import re
                
                # Extract JSON from markdown code blocks or find JSON object
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # Try to find JSON object in the response
                    json_match = re.search(r'\{.*?\}', response, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                    else:
                        json_str = response.strip()
                
                emotion = json.loads(json_str)
                return {
                    "valence": max(-1.0, min(1.0, emotion.get("valence", 0.0))),
                    "arousal": max(-1.0, min(1.0, emotion.get("arousal", 0.0))),
                    "dominance": max(-1.0, min(1.0, emotion.get("dominance", 0.0)))
                }
            except (json.JSONDecodeError, ValueError, AttributeError):
                logger.warning(f"Could not parse emotion analysis: {response}")
                return {"valence": 0.0, "arousal": 0.0, "dominance": 0.0}
                
        except Exception as e:
            logger.error(f"Error detecting emotion: {e}")
            return {"valence": 0.0, "arousal": 0.0, "dominance": 0.0}
    
    async def summarize_content(self, content: str, max_length: int = 100) -> str:
        """Summarize content for memory consolidation"""
        try:
            prompt = f"""
            Summarize the following content in {max_length} characters or less.
            Preserve the most important information and context.
            
            Content: {content}
            
            Summary:
            """
            
            messages = [{"role": "user", "content": prompt}]
            response = await self.chat_completion(
                messages, 
                temperature=0.3, 
                max_tokens=max_length // 3  # Rough estimate
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error summarizing content: {e}")
            return content[:max_length]  # Fallback to truncation
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between embeddings"""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Cosine similarity
            dot_product = np.dot(vec1, vec2)
            norms = np.linalg.norm(vec1) * np.linalg.norm(vec2)
            
            if norms == 0:
                return 0.0
            
            similarity = dot_product / norms
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0 