from openai import OpenAI as OpenAILLM
from spiral.llms.base import LLM
from typing import Any, Optional
from dotenv import load_dotenv
import logging
import sys
import os

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    level=logging.WARNING
)
logger = logging.getLogger('spiral.log')
load_dotenv()


class OpenAI(LLM):
    """A class for interacting with the OpenAI API.

    Args:
        model (str): The name of the OpenAI model to use
        temperature (float): The temperature to use when generating text
        api_key (str): Your OpenAI API key
        chat_history (list): Chat history
        max_tokens (int): The maximum number of tokens to generate in the completion
        supports_system_prompt (bool): Flag to indicate if system prompt should be supported
        system_prompt (str): System prompt to prepend to queries
    """
    
    model: str = 'gpt-4-turbo-preview'
    """model endpoint to use""" 
    
    vision_model: str = 'gpt-4-vision-preview'
    """vision model endpoint to use""" 
    
    temperature: float = 0.1
    """What sampling temperature to use.""" 
    
    api_key: str = os.getenv('OPENAI_API_KEY', '')
    """OpenAI API key""" 
    
    chat_history: list[str] = []
    """Chat history"""
    
    supports_system_prompt: bool = True
    """Flag to indicate if system prompt should be supported"""
    
    system_prompt: str = ""
    """System prompt to prepend to queries"""

    def __call__(self, query: dict, **kwds: dict)->Optional[str]:
        """Generates a response to a query using the OpenAI API.

        Args:
            query (dict): The query to generate a response to.
            kwds (dict): Additional keyword arguments to pass to the OpenAI API.

        Returns:
            A string containing the generated response.
        """

        client = OpenAILLM(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=self.temperature
        )
            
        return response.choices[0].message.content
