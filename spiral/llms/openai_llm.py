from openai import OpenAI
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


class GPT4(LLM):
    """A class for interacting with the OpenAI API.

    Args:
        model: The name of the OpenAI model to use.
        temperature: The temperature to use when generating text.
        api_key: Your OpenAI API key.
    """
    model: str = 'gpt-4-0125-preview'
    temperature: float = 0.1
    chat_history: list[str] = []
    api_key: str = os.getenv('OPENAI_API_KEY', '')

    def __call__(self, query, **kwds: Any)->str|None:
        """Generates a response to a query using the OpenAI API.

        Args:
        query: The query to generate a response to.
        kwds: Additional keyword arguments to pass to the OpenAI API.

        Returns:
        A string containing the generated response.
        """

        client = OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": query}
            ]
        )
            
        return response.choices[0].message.content
    
if __name__ == "__main__":
    try:
        assistant = GPT4()
        # assistant.add_tool(calculator)
        while True:
            message = input("\nEnter Query$ ")
            result = assistant(message)
            print(result)
    except KeyboardInterrupt:
        sys.exit(1)
