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

JavaDoc documentation generator using LLM.
Specialized layer for generating JavaDoc comments.
"""
import logging
from typing import Optional
from llm.llm_access import LLMAccessLayer
from config import LLMConfig


class JavaDocLLMGenerator:
    """Specialized generator for JavaDoc documentation using LLM."""
    
    def __init__(self, config: LLMConfig = None):
        """Initialize the JavaDoc generator."""
        self.llm_access = LLMAccessLayer(config)
        self.logger = logging.getLogger(__name__)
    
    def is_ready(self) -> bool:
        """Check if the generator is ready to use."""
        return (self.llm_access.is_service_available() and 
                self.llm_access.is_model_available())
    
    def generate_method_documentation(self, java_code: str, context: Optional[str] = None) -> Optional[str]:
        """
        Generate JavaDoc documentation for a Java method.
        
        Args:
            java_code: The Java method code
            context: Additional context about the method
            
        Returns:
            Generated JavaDoc string or None if generation failed
        """
        prompt = self._create_method_documentation_prompt(java_code, context)
        return self._generate_and_extract_javadoc(prompt)
    
    def generate_class_documentation(self, java_code: str, context: Optional[str] = None) -> Optional[str]:
        """
        Generate JavaDoc documentation for a Java class.
        
        Args:
            java_code: The Java class code
            context: Additional context about the class
            
        Returns:
            Generated JavaDoc string or None if generation failed
        """
        prompt = self._create_class_documentation_prompt(java_code, context)
        return self._generate_and_extract_javadoc(prompt)
    
    def generate_field_documentation(self, java_code: str, context: Optional[str] = None) -> Optional[str]:
        """
        Generate JavaDoc documentation for a Java field.
        
        Args:
            java_code: The Java field code
            context: Additional context about the field
            
        Returns:
            Generated JavaDoc string or None if generation failed
        """
        prompt = self._create_field_documentation_prompt(java_code, context)
        return self._generate_and_extract_javadoc(prompt)
    
    def _generate_and_extract_javadoc(self, prompt: str) -> Optional[str]:
        """Generate response and extract JavaDoc from it."""
        response = self.llm_access.generate_response(
            prompt=prompt,
            stop_sequences=['```', 'Java Code:', 'Context:', 'Example:']
        )
        
        if response:
            documentation = self._extract_javadoc(response)
            if documentation:
                self.logger.debug("Successfully generated JavaDoc documentation")
                return documentation
            else:
                self.logger.warning("Failed to extract valid JavaDoc from response")
        
        return None
    
    def _create_method_documentation_prompt(self, java_code: str, context: Optional[str] = None) -> str:
        """Create a prompt for method documentation generation."""
        prompt = """You are a Java documentation expert. Generate a proper JavaDoc comment for the following Java method.

Rules:
1. Generate ONLY the JavaDoc comment (/** ... */)
2. Include @param tags for all parameters with clear descriptions
3. Include @return tag if method returns something other than void
4. Include @throws tags for checked exceptions if applicable
5. Write clear, concise descriptions of what the method does
6. Do not include the code itself in your response
7. Start with /** and end with */
8. Use proper JavaDoc formatting

"""
        
        if context:
            prompt += f"Context: {context}\n\n"
        
        prompt += f"Java Method:\n{java_code}\n\nGenerate JavaDoc:"
        
        return prompt
    
    def _create_class_documentation_prompt(self, java_code: str, context: Optional[str] = None) -> str:
        """Create a prompt for class documentation generation."""
        prompt = """You are a Java documentation expert. Generate a proper JavaDoc comment for the following Java class.

Rules:
1. Generate ONLY the JavaDoc comment (/** ... */)
2. Describe the purpose and responsibility of the class
3. Include @author tag if appropriate
4. Include @since tag if version information is available
5. Include @see tags for related classes if relevant
6. Write clear, concise descriptions
7. Do not include the code itself in your response
8. Start with /** and end with */
9. Use proper JavaDoc formatting

"""
        
        if context:
            prompt += f"Context: {context}\n\n"
        
        prompt += f"Java Class:\n{java_code}\n\nGenerate JavaDoc:"
        
        return prompt
    
    def _create_field_documentation_prompt(self, java_code: str, context: Optional[str] = None) -> str:
        """Create a prompt for field documentation generation."""
        prompt = """You are a Java documentation expert. Generate a proper JavaDoc comment for the following Java field.

Rules:
1. Generate ONLY the JavaDoc comment (/** ... */)
2. Describe the purpose and usage of the field
3. Include information about field constraints if applicable
4. Write clear, concise descriptions
5. Do not include the code itself in your response
6. Start with /** and end with */
7. Use proper JavaDoc formatting

"""
        
        if context:
            prompt += f"Context: {context}\n\n"
        
        prompt += f"Java Field:\n{java_code}\n\nGenerate JavaDoc:"
        
        return prompt
    
    def _extract_javadoc(self, response: str) -> Optional[str]:
        """Extract and clean JavaDoc from the LLM response."""
        if not response:
            return None
        
        # Remove any markdown code blocks
        response = response.replace("```java", "").replace("```", "")
        
        # Find the JavaDoc comment
        lines = response.split('\n')
        javadoc_lines = []
        in_javadoc = False
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('/**'):
                in_javadoc = True
                javadoc_lines.append(line)
            elif in_javadoc:
                javadoc_lines.append(line)
                if line.endswith('*/'):
                    break
        
        if not javadoc_lines:
            # If no proper JavaDoc found, try to create one from the response
            cleaned_response = response.strip()
            if cleaned_response and not cleaned_response.startswith('/**'):
                return f"/**\n * {cleaned_response}\n */"
            elif cleaned_response:
                return cleaned_response
            return None
        
        javadoc = '\n'.join(javadoc_lines)
        
        # Basic validation
        if '/**' in javadoc and '*/' in javadoc:
            return javadoc
        
        return None
    
    def pull_model_if_needed(self) -> bool:
        """Pull the model if it's not available."""
        return self.llm_access.pull_model()
    
    def list_available_models(self) -> list:
        """Get a list of available models."""
        return self.llm_access.list_available_models()