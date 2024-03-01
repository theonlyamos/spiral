import cohere
from spiral.llms.base import LLM
from typing import Any, Optional
from dotenv import load_dotenv
import logging
import sys
import os
import ast

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    level=logging.INFO
)
logger = logging.getLogger('spiral.log')
load_dotenv()

class Cohere(LLM):
    """A class for interacting with the Cohere API.

    Args:
        model: The name of the Cohere model to use.
        temperature: The temperature to use when generating text.
        api_key: Your Cohere API key.
    """
    model: str = 'command-nightly'
    """model endpoint to use""" 
    
    temperature: float = 0.1
    """What sampling temperature to use.""" 
    
    chat_history: list[str] = []
    """Chat history"""
    
    api_key: str = os.getenv('CO_API_KEY', '')
    """Cohere API key""" 

    def __call__(self, query, **kwds: Any)->str:
        """Generates a response to a query using the Cohere API.

        Args:
        query: The query to generate a response to.
        kwds: Additional keyword arguments to pass to the Cohere API.

        Returns:
        A string containing the generated response.
        """

        client = cohere.Client(api_key=self.api_key)
        response = client.chat( 
            model=self.model,
            message=query,
            temperature=self.temperature,
            prompt_truncation='auto',
            stream=False,
            citation_quality='accurate',
            connectors=[{"id": "web-search"}]
        )
            
        return response.text
    
if __name__ == "__main__":
    try:
        assistant = Cohere()
        # assistant.add_tool(calculator)
        while True:
            message = input("\nEnter Query$ ")
            result = assistant(message)
            print(result)
    except KeyboardInterrupt:
        sys.exit(1)
