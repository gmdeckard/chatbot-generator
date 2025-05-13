import requests
from typing import Dict, List, Any, Optional
import logging
import os
import json
from pathlib import Path

# Import config if available
try:
    from src.config import get_llm_config
    llm_config = get_llm_config()
    DEFAULT_SYSTEM_PROMPT = llm_config.get("system_prompt", "You are a helpful assistant.")
    DEFAULT_PARAMS = llm_config.get("parameters", {})
except ImportError:
    DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."
    DEFAULT_PARAMS = {
        "temperature": 0.7,
        "top_k": 40,
        "top_p": 0.9,
        "max_tokens": 1024
    }

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaLLM:
    def __init__(self, model_name: str = "{{ model_name }}", base_url: str = "http://ollama:11434"):
        """
        Initialize the Ollama LLM client with {{ model_name }}
        
        Args:
            model_name: Name of the model to use
            base_url: Base URL for the Ollama API
        """
        self.model_name = model_name
        self.base_url = base_url
        self.generate_api = f"{base_url}/api/generate"
        logger.info(f"Initialized Ollama client with model: {model_name}")
        
    def generate_response(self, 
                         prompt: str, 
                         system_prompt: Optional[str] = None,
                         context: Optional[List[Dict[str, str]]] = None,
                         **kwargs) -> str:
        """
        Generate a response from the LLM
        
        Args:
            prompt: User's input message
            system_prompt: Optional system prompt to guide the model
            context: Previous conversation history
            **kwargs: Additional parameters to override defaults
            
        Returns:
            The model's response as a string
        """
        # Start with default parameters
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }
        
        # Add custom parameters from config
        for param, value in DEFAULT_PARAMS.items():
            payload[param] = value
            
        # Override with any kwargs provided
        for param, value in kwargs.items():
            payload[param] = value
        
        # Add system prompt and context if provided
        if system_prompt:
            payload["system"] = system_prompt
        else:
            payload["system"] = DEFAULT_SYSTEM_PROMPT
            
        if context:
            payload["context"] = context
            
        try:
            logger.info(f"Sending request to Ollama API")
            response = requests.post(self.generate_api, json=payload)
            response.raise_for_status()
            result = response.json().get("response", "")
            logger.info(f"Received response from Ollama")
            return result
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"Error generating response: {str(e)}"
            
    def health_check(self) -> bool:
        """Check if the Ollama service is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception:
            return False
            
    def analyze_code(self, code_block: str) -> str:
        """
        Analyze a code block
        
        Args:
            code_block: The code to analyze
            
        Returns:
            Analysis of the code as a string
        """
        prompt = f"Please analyze this code and provide insights or improvements:\n\n```\n{code_block}\n```"
        return self.generate_response(prompt=prompt, temperature=0.3)
