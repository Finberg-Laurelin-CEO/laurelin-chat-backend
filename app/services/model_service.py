import os
import openai
import google.generativeai as genai
from typing import Dict, Any, List, Optional
from app.config import Config
from app.services.llm_integration_service import LLMIntegrationService

class ModelService:
    """Service for communicating with different AI models"""
    
    def __init__(self):
        # Initialize OpenAI
        openai.api_key = Config.OPENAI_API_KEY
        
        # Initialize Google AI
        genai.configure(api_key=Config.GOOGLE_AI_API_KEY)
        self.google_model = genai.GenerativeModel('gemini-pro')
        
        # Initialize LLM integration service
        self.llm_integration = LLMIntegrationService()
    
    def generate_response_openai(self, messages: List[Dict[str, str]], 
                               model: str = "gpt-3.5-turbo") -> Dict[str, Any]:
        """Generate response using OpenAI GPT models"""
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return {
                'success': True,
                'content': response.choices[0].message.content,
                'model': model,
                'usage': response.usage,
                'metadata': {
                    'provider': 'openai',
                    'model': model
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'model': model,
                'metadata': {
                    'provider': 'openai',
                    'model': model
                }
            }
    
    def generate_response_google(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate response using Google Gemini model"""
        try:
            # Convert messages to prompt format for Gemini
            prompt = self._convert_messages_to_prompt(messages)
            
            response = self.google_model.generate_content(prompt)
            
            return {
                'success': True,
                'content': response.text,
                'model': 'gemini-pro',
                'metadata': {
                    'provider': 'google',
                    'model': 'gemini-pro'
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'model': 'gemini-pro',
                'metadata': {
                    'provider': 'google',
                    'model': 'gemini-pro'
                }
            }
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert chat messages to a single prompt for Gemini"""
        prompt_parts = []
        
        for message in messages:
            role = message['role']
            content = message['content']
            
            if role == 'system':
                prompt_parts.append(f"System: {content}")
            elif role == 'user':
                prompt_parts.append(f"User: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}")
        
        return "\n\n".join(prompt_parts)
    
    def generate_response(self, messages: List[Dict[str, str]], 
                         model_provider: str = "openai", session_id: str = None,
                         user_id: str = None, use_llm_backend: bool = True) -> Dict[str, Any]:
        """Generate response using specified model provider"""
        
        # If using LLM backend and we have session/user info, use Pub/Sub
        if use_llm_backend and session_id and user_id:
            return self.generate_response_via_llm_backend(
                messages, model_provider, session_id, user_id
            )
        
        # Fallback to direct API calls
        if model_provider.lower() == "openai":
            return self.generate_response_openai(messages)
        elif model_provider.lower() == "google":
            return self.generate_response_google(messages)
        else:
            return {
                'success': False,
                'error': f"Unsupported model provider: {model_provider}",
                'metadata': {
                    'provider': model_provider
                }
            }
    
    def generate_response_via_llm_backend(self, messages: List[Dict[str, str]], 
                                         model_provider: str, session_id: str, 
                                         user_id: str) -> Dict[str, Any]:
        """Generate response via LLM backend using Pub/Sub"""
        try:
            # Publish request to LLM backend
            success = self.llm_integration.publish_llm_request(
                session_id=session_id,
                user_id=user_id,
                messages=messages,
                model_provider=model_provider
            )
            
            if success:
                return {
                    'success': True,
                    'content': 'Request sent to LLM backend for processing',
                    'model': model_provider,
                    'metadata': {
                        'provider': 'llm-backend',
                        'processing': 'async',
                        'session_id': session_id
                    }
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to send request to LLM backend',
                    'metadata': {
                        'provider': 'llm-backend'
                    }
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"LLM backend integration error: {str(e)}",
                'metadata': {
                    'provider': 'llm-backend'
                }
            }
    
    def generate_response_ab_test(self, messages: List[Dict[str, str]], 
                                 session_id: str, user_id: str) -> Dict[str, Any]:
        """Generate response using A/B testing via LLM backend"""
        try:
            success = self.llm_integration.publish_ab_test_request(
                session_id=session_id,
                user_id=user_id,
                messages=messages
            )
            
            if success:
                return {
                    'success': True,
                    'content': 'A/B test request sent to LLM backend',
                    'model': 'ab-test',
                    'metadata': {
                        'provider': 'llm-backend',
                        'ab_test': True,
                        'processing': 'async',
                        'session_id': session_id
                    }
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to send A/B test request to LLM backend',
                    'metadata': {
                        'provider': 'llm-backend',
                        'ab_test': True
                    }
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"A/B test integration error: {str(e)}",
                'metadata': {
                    'provider': 'llm-backend',
                    'ab_test': True
                }
            }
