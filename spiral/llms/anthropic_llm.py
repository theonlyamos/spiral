from spiral.llms.base import LLM
from typing import Any
from dotenv import load_dotenv
import anthropic
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


class Claude(LLM):
    """A class for interacting with the Claude API.

    Args:
        model: The name of the Claude model to use.
        temperature: The temperature to use when generating text.
        api_key: Your Anthropic API key.
    """
    model: str = 'claude-3-sonnet-20240229'
    """model endpoint to use""" 
    
    temperature: float = 0.1
    """What sampling temperature to use.""" 
    
    chat_history: list[str] = []
    """Chat history"""
    
    api_key: str = os.getenv('ANTHROPIC_API_KEY', '')
    """ANTHROPIC API key""" 
    
    max_tokens: int = 4000
    """The maximum number of tokens to generate in the completion.""" 
    
    supports_system_prompt: bool = True
    """Flag to indicate if system prompt should be supported"""
    
    def format_query(self, message: dict[str, str]) -> list:
        """Formats a message for the Cohere API"""
        formatted_message = self.chat_history.copy()
        formatted_message.append(message) # type: ignore
        
        messages = [
            {
                "role": "user",
                "content": []
            },
            {
                "role": "assistant",
                "content": []
            }
        ]
        
        for fm in formatted_message:
            new_message = {}
            if fm['type'] == 'text': # type: ignore
                new_message = {
                    'type': fm['type'], # type: ignore
                    'text': fm['message'] # type: ignore
                }
            else:
                new_message = {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": fm['image'] # type: ignore
                }
            }
            
            if fm['role'].lower() == 'user': # type: ignore
                messages[0]['content'].append(new_message)
            else:
                messages[1]['content'].append(new_message)

        return messages

    def __call__(self, query, **kwds: Any)->list|str|None:
        """Generates a response to a query using the Claude API.

        Args:
        query: The query to generate a response to.
        kwds: Additional keyword arguments to pass to the Claude API.

        Returns:
        A string containing the generated response.
        """

        client = anthropic.Anthropic(api_key=self.api_key)
        result = client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=self.system_prompt,
            messages=self.format_query(query)
        )
        
        return result.content[0].text     

if __name__ == "__main__":
    try:
        assistant = Claude()
        while True:
            message = input("\nEnter Query$ ")
            result = assistant(message)
            print(result)
    except KeyboardInterrupt:
        sys.exit(1)