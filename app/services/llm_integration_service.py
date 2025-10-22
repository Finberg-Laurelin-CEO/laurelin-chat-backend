import json
import base64
from typing import Dict, Any, Optional
from google.cloud import pubsub_v1
from app.config import Config

class LLMIntegrationService:
    """Service for integrating with the LLM backend via Pub/Sub"""
    
    def __init__(self):
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_name = f"projects/{Config.GOOGLE_CLOUD_PROJECT}/topics/llm-processing"
    
    def publish_llm_request(self, session_id: str, user_id: str, messages: list, 
                           model_provider: str = None, model_name: str = None,
                           temperature: float = 0.7, max_tokens: int = 1000) -> bool:
        """Publish an LLM request to the processing queue"""
        try:
            # Prepare the LLM request payload
            llm_request = {
                "session_id": session_id,
                "user_id": user_id,
                "messages": messages,
                "model_provider": model_provider,
                "model_name": model_name,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False,
                "metadata": {
                    "source": "flask-backend",
                    "timestamp": str(datetime.utcnow())
                }
            }
            
            # Convert to JSON and encode
            message_data = json.dumps(llm_request).encode('utf-8')
            
            # Publish to Pub/Sub
            future = self.publisher.publish(
                self.topic_name,
                message_data,
                session_id=session_id,
                user_id=user_id
            )
            
            # Wait for the publish to complete
            message_id = future.result()
            print(f"Published LLM request {message_id} for session {session_id}")
            
            return True
            
        except Exception as e:
            print(f"Error publishing LLM request: {e}")
            return False
    
    def publish_ab_test_request(self, session_id: str, user_id: str, messages: list,
                               experiment_name: str = "model_comparison") -> bool:
        """Publish an A/B test LLM request"""
        try:
            # For A/B testing, we don't specify a model provider
            # The LLM backend will determine the provider based on user assignment
            return self.publish_llm_request(
                session_id=session_id,
                user_id=user_id,
                messages=messages,
                model_provider=None,  # Let LLM backend decide
                metadata={
                    "ab_test_experiment": experiment_name,
                    "source": "flask-backend"
                }
            )
        except Exception as e:
            print(f"Error publishing A/B test request: {e}")
            return False
