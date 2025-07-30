"""
Core AI interface for LLM interactions with structured outputs via Braintrust proxy.
"""

import os
from typing import Any, Dict, List, Optional, Type, TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel

from .specify_model import specify_ai_model

T = TypeVar('T', bound=BaseModel)

class AIClient:
    """AI client that provides structured outputs via OpenAI's beta.chat.completions.parse"""

    def __init__(self, client: AsyncOpenAI, model: str, temperature: float):
        self.client = client
        self.model = model
        self.temperature = temperature

    async def gen_obj(
        self,
        schema: Type[T],
        messages: List[Dict[str, Any]],
        temperature: Optional[float] = None
    ) -> T:
        """
        Generate structured output using OpenAI's beta.chat.completions.parse
        
        Args:
            schema: Pydantic model class to structure the response
            messages: List of message dictionaries for the conversation
            temperature: Temperature for the model (defaults to what was set in create_ai)
            
        Returns:
            Instance of the schema class with the parsed response
        """
        # Prepare the API call parameters
        call_params = {
            "model": specify_ai_model(self.model),
            "messages": messages,
            "response_format": schema,
        }

        # Add temperature if specified or use the default from the client
        if temperature is not None:
            call_params["temperature"] = temperature
        else:
            call_params["temperature"] = self.temperature

        try:
            # Use OpenAI's structured output parsing
            response = await self.client.beta.chat.completions.parse(**call_params)

            # Check if the model refused to respond
            if response.choices[0].message.refusal:
                raise Exception(f"Model refused to respond: {response.choices[0].message.refusal}")

            # Return the parsed object
            parsed_result = response.choices[0].message.parsed
            if parsed_result is None:
                raise Exception("Failed to parse response into structured format")

            return parsed_result

        except Exception as e:
            raise Exception(f"Failed to generate structured output: {str(e)}")


def create_ai(
    model: str = "gpt-4o",
    temperature: float = 0.0,
    braintrust_api_key: Optional[str] = None
) -> AIClient:
    """
    Create an AI client configured to use Braintrust proxy with structured outputs.
    
    Args:
        model: Model to use (defaults to gpt-4o)
        temperature: Temperature for model responses
        braintrust_api_key: Braintrust API key (if not provided, tries environment variable)
        
    Returns:
        AIClient instance with gen_obj method for structured outputs
        
    Raises:
        Exception: If no API key can be obtained
    """
    # Get API key from parameter or environment
    api_key = braintrust_api_key or os.getenv("BRAINTRUST_API_KEY")
    
    if not api_key:
        raise Exception("Braintrust API key is required. Provide it as a parameter or set BRAINTRUST_API_KEY environment variable.")
    
    # Get optional base URL from environment
    base_url = os.getenv("BRAINTRUST_BASE_URL", "https://api.braintrust.dev/v1/proxy")

    # Create AsyncOpenAI client configured for Braintrust proxy
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url
    )

    return AIClient(client, model, temperature)
