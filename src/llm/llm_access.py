"""
Copyright (C) 2025 Roland Spatzenegger

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Technical LLM access layer for interacting with Ollama.
This is a generic layer that can be used for various LLM tasks.
"""
import logging
from typing import Optional, Dict, Any, List
import ollama
from config import LLMConfig


class LLMAccessLayer:
    """Generic technical layer for interacting with Ollama API."""
    
    def __init__(self, config: LLMConfig = None):
        """Initialize the LLM access layer."""
        self.config = config or LLMConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize the ollama client with custom host if specified
        self.client = ollama.Client(host=self.config.host)
    
    def is_service_available(self) -> bool:
        """Check if Ollama service is available."""
        try:
            self.client.list()
            return True
        except Exception as e:
            self.logger.debug(f"Ollama service check failed: {e}")
            return False
    
    def is_model_available(self, model_name: str = None) -> bool:
        """
        Check if the specified model is available.
        
        Args:
            model_name: Model name to check, defaults to config model
            
        Returns:
            True if model is available, False otherwise
        """
        model_to_check = model_name or self.config.model
        
        try:
            models = self.client.list()
            model_names = [model.model for model in models.get('models', [])]
            
            # Check if exact model name exists or if it's a partial match
            for available_model in model_names:
                if (model_to_check in available_model or 
                    available_model.startswith(model_to_check)):
                    return True
            
            self.logger.warning(
                f"Model '{model_to_check}' not found. Available models: {model_names}"
            )
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to check model availability: {e}")
            return False
    
    def generate_response(self, 
                         prompt: str, 
                         model: str = None,
                         stream: bool = False,
                         temperature: float = None,
                         top_p: float = None,
                         stop_sequences: List[str] = None,
                         max_retries: int = None) -> Optional[str]:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The input prompt
            model: Model to use, defaults to config model
            stream: Whether to stream the response
            temperature: Sampling temperature, defaults to config value
            top_p: Top-p sampling parameter, defaults to config value
            stop_sequences: List of stop sequences
            max_retries: Maximum retry attempts, defaults to config value
            
        Returns:
            Generated response string or None if failed
        """
        model_name = model or self.config.model
        temp = temperature if temperature is not None else self.config.temperature
        top_p_val = top_p if top_p is not None else self.config.top_p
        retries = max_retries if max_retries is not None else self.config.max_retries
        
        # Check if model is available before proceeding
        if not self.is_model_available(model_name):
            self.logger.error(f"Model '{model_name}' is not available")
            return None
        
        for attempt in range(retries):
            try:
                self.logger.debug(f"Making LLM request (attempt {attempt + 1}/{retries})")
                
                options = {
                    'temperature': temp,
                    'top_p': top_p_val,
                }
                
                if stop_sequences:
                    options['stop'] = stop_sequences
                # self.logger.debug(f"Prompt: {prompt}")
                response = self.client.generate(
                    model=model_name,
                    prompt=prompt,
                    stream=stream,
                    options=options
                )
                
                if stream:
                    # Handle streaming response
                    return self._handle_streaming_response(response)
                else:
                    # Handle non-streaming response
                    result = response.get('response', '').strip()
                    if result:
                        self.logger.debug("Successfully generated LLM response")
                        return result
                
            except ollama.ResponseError as e:
                self.logger.warning(f"Ollama API error on attempt {attempt + 1}: {e}")
                if attempt == retries - 1:
                    self.logger.error("All attempts failed due to API errors")
            except Exception as e:
                self.logger.warning(f"Request failed on attempt {attempt + 1}: {e}")
                if attempt == retries - 1:
                    self.logger.error("All attempts failed to generate response")
        
        return None
    
    def _handle_streaming_response(self, response) -> str:
        """Handle streaming response from Ollama."""
        full_response = ""
        try:
            for chunk in response:
                if 'response' in chunk:
                    full_response += chunk['response']
            return full_response.strip()
        except Exception as e:
            self.logger.error(f"Error handling streaming response: {e}")
            return ""
    
    def pull_model(self, model_name: str = None) -> bool:
        """
        Pull the specified model if it's not available.
        
        Args:
            model_name: Model name to pull, defaults to config model
            
        Returns:
            True if model was successfully pulled or already available, False otherwise
        """
        model_to_pull = model_name or self.config.model
        
        try:
            if self.is_model_available(model_to_pull):
                self.logger.info(f"Model '{model_to_pull}' is already available")
                return True
            
            self.logger.info(f"Pulling model '{model_to_pull}'...")
            self.client.pull(model_to_pull)
            self.logger.info(f"Successfully pulled model '{model_to_pull}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to pull model '{model_to_pull}': {e}")
            return False
    
    def list_available_models(self) -> List[str]:
        """
        Get a list of available models.
        
        Returns:
            List of available model names
        """
        try:
            models = self.client.list()
            return [model.model for model in models.get('models', [])]
        except Exception as e:
            self.logger.error(f"Failed to list models: {e}")
            return []
    
    def get_model_info(self, model_name: str = None) -> Optional[Dict[str, Any]]:
        """
        Get information about the specified model.
        
        Args:
            model_name: Model name to get info for, defaults to config model
            
        Returns:
            Dictionary with model information or None if not available
        """
        model_to_check = model_name or self.config.model
        
        try:
            models = self.client.list()
            for model in models.get('models', []):
                model_name_in_list = model.model
                if (model_to_check in model_name_in_list or 
                    model_name_in_list.startswith(model_to_check)):
                    return model
            return None
        except Exception as e:
            self.logger.error(f"Failed to get model info: {e}")
            return None
    
    def chat_completion(self, 
                       messages: List[Dict[str, str]], 
                       model: str = None,
                       temperature: float = None,
                       top_p: float = None) -> Optional[str]:
        """
        Generate a chat completion response.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use, defaults to config model
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            
        Returns:
            Generated response string or None if failed
        """
        model_name = model or self.config.model
        temp = temperature if temperature is not None else self.config.temperature
        top_p_val = top_p if top_p is not None else self.config.top_p
        
        try:
            response = self.client.chat(
                model=model_name,
                messages=messages,
                options={
                    'temperature': temp,
                    'top_p': top_p_val,
                }
            )
            
            return response.get('message', {}).get('content', '').strip()
            
        except Exception as e:
            self.logger.error(f"Chat completion failed: {e}")
            return None