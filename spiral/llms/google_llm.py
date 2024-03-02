from spiral.llms.base import LLM
from typing import Any
import google.generativeai as genai
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


class Gemini(LLM):
    """A class for interacting with the Gemini API.

    Args:
        model: The name of the Gemini model to use.
        temperature: The temperature to use when generating text.
        api_key: Your Google API key.
    """
    model: str = 'gemini-pro'
    """model endpoint to use""" 
    
    temperature: float = 0.1
    """What sampling temperature to use.""" 
    
    chat_history: list[str] = []
    """Chat history"""
    
    api_key: str = os.getenv('GOOGLE_API_KEY', '')
    """GOOGLE API key""" 
    
    supports_system_prompt: bool = True
    """Flag to indicate if system prompt should be supported"""
    
    system_prompt: str = ""
    """System prompt to prepend to queries"""

    def __call__(self, query, **kwds: Any)->str|None:
        """Generates a response to a query using the Gemini API.

        Args:
        query: The query to generate a response to.
        kwds: Additional keyword arguments to pass to the Gemini API.

        Returns:
        A string containing the generated response.
        """
        genai.configure(api_key=self.api_key)

        client = genai.GenerativeModel(self.model)
        
        general_config = {
            "max_output_tokens": 2048,
            "temperature": self.temperature,
            "top_p": 1,
            "top_k": 32
        }
        
        response = client.generate_content(
            [query],
            stream=True,
            generation_config=general_config    # type: ignore
        )
        response.resolve()
        result = response.text
            
        return result
    
if __name__ == "__main__":
    try:
        assistant = Gemini()
        # assistant.add_tool(calculator)
        while True:
            message = input("\nEnter Query$ ")
            result = assistant(message)
            print(result)
    except KeyboardInterrupt:
        sys.exit(1)
