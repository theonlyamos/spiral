from pydantic import BaseModel, Field
from typing import Any, List, Dict
import logging
import json

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    level=logging.INFO
)
logger = logging.getLogger('spiral.log')

PROMPT_TEMPLATE = """
You are a helpful, respectful and honest assistant.
Always answer as helpfully as possible, while being safe.
Your answers should not include any harmful, unethical,
racist, sexist, toxic, dangerous, or illegal content.

Please ensure your responses are socially unbiased and
positive in nature.

If a question does not make any sense, or is not factually coherent,
explain why instead of answering something not corrent.

Always check your answer against the current results from the
current search tool.
Always return the most updated and correct answer.
If you do not come up with any answer, just tell me you don't know.

Never share false information

The chatbot assistant can perform a variety of tasks, including:
Answering questions in a comprehensive and informative way
Generating different creative text formats of text content
Translating languages
Performing mathematical calculations
Summarizing text
Accessing and using external tools

Tools:
{tools}

The chatbot assistant should always follow chain of thought reasoning and use its knowledge and abilities to provide the best possible response to the user.

Use the following format:

query: the input query you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of {available_tools}
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input query

Begin!

query: {query}
Thought:

The response should be in a valid json format which can
be directed converted into a python dictionary with 
json.loads()
Return the response in the following format:
{
  "thought": "{thought}",
  "action": "{action}",
  "action_input": "{action_input}",
  "observation": "{observation}",
  "final_answer": "{actionable_response}"
}
"""

class LLM(BaseModel):
    """
    A class for representing a large language model.

    Args:
        model: The name of the language model to use.
        temperature: The temperature to use when generating text.
        api_key: The API Key of the model.
        max_tokens: The maximum number of tokens to generate in the completion.
    """

    model: str = Field(default=None)
    """model endpoint to use""" 
  
    temperature: float = Field(default=0.4)
    """What sampling temperature to use.""" 

    api_key: str = Field(default=None)
    """API key""" 
    
    max_tokens: int = Field(default=512)
    """The maximum number of tokens to generate in the completion.""" 

