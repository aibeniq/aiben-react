"""
Session management with Redis backend for persistent storage.
Handles complex objects like retrievers and LLMs that can't be directly serialized.
"""
import json
import os
import redis
import threading
import uuid
from datetime import datetime
from typing import Any, Dict, Optional


class SessionManager:
    """
    Redis-backed session manager with fallback to in-memory storage.
    
    For complex objects that can't be serialized (like LangChain retrievers and LLMs),
    we store metadata and rebuild them as needed.
    """
    
    def __init__(self):
        self.default_ttl = 1800  # 30 minutes
        
        # Try to connect to Redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            print(f"SessionManager: Connected to Redis at {redis_url}")
            self.use_redis = True
        except Exception as e:
            print(f"SessionManager: Failed to connect to Redis ({e}), using in-memory fallback")
            self.use_redis = False
            self._init_memory_cache()
    
    def _init_memory_cache(self):
        """Initialize in-memory cache as fallback"""
        self.cache = {}
        self.lock = threading.Lock()
        self.expiry = {}
    
    def _serialize_session_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Serialize session data for Redis storage.
        
        Complex objects are replaced with metadata that can be used to rebuild them.
        """
        serializable = {}
        
        for key, value in data.items():
            if key == "retriever" and value is not None:
                # Store retriever metadata instead of the object
                serializable[key] = {
                    "type": "retriever",
                    "created_at": datetime.now().isoformat(),
                    "needs_rebuild": True
                }
            elif key == "llm" and value is not None:
                # Store LLM metadata instead of the object
                serializable[key] = {
                    "type": "llm", 
                    "created_at": datetime.now().isoformat(),
                    "needs_rebuild": True
                }
            elif key == "vectorstore" and value is not None:
                # Store vectorstore metadata instead of the object
                serializable[key] = {
                    "type": "vectorstore",
                    "created_at": datetime.now().isoformat(), 
                    "needs_rebuild": True
                }
            else:
                # Try to serialize the value
                try:
                    json.dumps(value)
                    serializable[key] = value
                except (TypeError, ValueError):
                    # Skip non-serializable values
                    print(f"SessionManager: Skipping non-serializable key: {key}")
                    continue
        
        return serializable
    
    def _deserialize_session_data(self, data: str) -> Optional[Dict[str, Any]]:
        """Deserialize session data from Redis"""
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return None
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by ID"""
        if self.use_redis:
            try:
                data = self.redis_client.get(f"session:{session_id}")
                if data:
                    return self._deserialize_session_data(data)
                return None
            except Exception as e:
                print(f"SessionManager Redis get error: {e}")
                return None
        else:
            # In-memory fallback
            with self.lock:
                if session_id in self.cache:
                    self.expiry[session_id] = datetime.now()
                    return self.cache[session_id]
            return None
    
    def set_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Set session data"""
        if self.use_redis:
            try:
                serializable_data = self._serialize_session_data(data)
                self.redis_client.setex(
                    f"session:{session_id}",
                    self.default_ttl,
                    json.dumps(serializable_data)
                )
                return True
            except Exception as e:
                print(f"SessionManager Redis set error: {e}")
                return False
        else:
            # In-memory fallback
            with self.lock:
                self.cache[session_id] = data
                self.expiry[session_id] = datetime.now()
            return True
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session data"""
        if self.use_redis:
            try:
                self.redis_client.delete(f"session:{session_id}")
                return True
            except Exception as e:
                print(f"SessionManager Redis delete error: {e}")
                return False
        else:
            # In-memory fallback
            with self.lock:
                if session_id in self.cache:
                    del self.cache[session_id]
                if session_id in self.expiry:
                    del self.expiry[session_id]
            return True
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions (only needed for in-memory fallback)"""
        if not self.use_redis:
            now = datetime.now()
            with self.lock:
                expired = [
                    sid for sid, time in self.expiry.items()
                    if (now - time).seconds > self.default_ttl
                ]
                for sid in expired:
                    if sid in self.cache:
                        del self.cache[sid]
                    if sid in self.expiry:
                        del self.expiry[sid]
    
    def session_needs_rebuild(self, session_data: Dict[str, Any], component: str) -> bool:
        """
        Check if a session component needs to be rebuilt after Redis deserialization.
        
        Args:
            session_data: The session data dictionary
            component: The component to check ('retriever', 'llm', 'vectorstore')
            
        Returns:
            True if the component needs rebuilding, False otherwise
        """
        if not session_data or component not in session_data:
            return True
        
        component_data = session_data[component]
        
        # If component is None, it needs rebuilding
        if component_data is None:
            return True
        
        # If component is a metadata dict (from Redis serialization), it needs rebuilding
        if isinstance(component_data, dict) and component_data.get("needs_rebuild"):
            return True
        
        # Check if component is a basic type (string, int, etc.) - means it got serialized
        if isinstance(component_data, (str, int, float, bool, list)):
            print(f"Component {component} is basic type {type(component_data)} - needs rebuilding")
            return True
        
        # For complex objects, check if they have required methods/attributes
        if component == "retriever":
            has_method = hasattr(component_data, "get_relevant_documents")
            if not has_method:
                print(f"Retriever missing get_relevant_documents method - needs rebuilding")
            return not has_method
        elif component == "llm":
            has_invoke = hasattr(component_data, "invoke")
            has_generate = hasattr(component_data, "generate") 
            has_method = has_invoke or has_generate
            if not has_method:
                print(f"LLM missing invoke/generate methods - needs rebuilding")
            return not has_method
        elif component == "vectorstore":
            has_method = hasattr(component_data, "similarity_search")
            if not has_method:
                print(f"Vectorstore missing similarity_search method - needs rebuilding")
            return not has_method
            
        return False


# Global session manager instance
session_manager = SessionManager()
