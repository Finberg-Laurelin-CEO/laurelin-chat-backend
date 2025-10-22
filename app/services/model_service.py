import os
import openai
import google.generativeai as genai
from typing import Dict, Any, List, Optional
from app.config import Config

class ModelService:
    """Service for communicating with different AI models"""
    
    def __init__(self):
        # Initialize OpenAI
        openai.api_key = Config.OPENAI_API_KEY
        
        # Initialize Google AI
        genai.configure(api_key=Config.GOOGLE_AI_API_KEY)
        self.google_model = genai.GenerativeModel('gemini-pro')
    
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
                         model_provider: str = "openai") -> Dict[str, Any]:
        """Generate response using specified model provider"""
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
