import os
import sys
import logging
import together 
from ..llms.base import LLM
from dotenv import load_dotenv
from pydantic import Extra, Field, root_validator
from typing import Any, Dict, List, Mapping, Optional 

load_dotenv()

B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
DEFAULT_SYSTEM_PROMPT = """
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
"""

def get_prompt(instruction, new_system_prompt=DEFAULT_SYSTEM_PROMPT ):
    SYSTEM_PROMPT = B_SYS + new_system_prompt + E_SYS
    prompt_template = B_INST + SYSTEM_PROMPT + instruction + E_INST
    
    return prompt_template

def cut_off_text(text, prompt):
    cutoff_phrase = prompt
    index = text.find(cutoff_phrase)
    if index != -1:
        return text[:index]
    else:
        return text

class TogetherLLM(LLM):
    """Together large language models.""" 
    
    model: str = "togethercomputer/llama-2-70b-chat"
    """model endpoint to use""" 

    api_key: str = os.environ["TOGETHER_API_KEY"]
    """Together API key""" 

    temperature: float = 0.1
    """What sampling temperature to use.""" 
    
    max_tokens: int = 512
    """The maximum number of tokens to generate in the completion.""" 

    class Config:
        extra = 'allow'
    
    # @root_validator()
    # def validate_environment(cls, values: Dict) -> Dict:
    #     """Validate that the API key is set."""
    #     # api_key = get_from_dict_or_env(
    #     #     values, "api_key", "TOGETHER_API_KEY"
    #     # )
    #     values["api_key"] = cls.api_key
    #     return values
    
    @property
    def _llm_type(self) -> str:
        """Return type of LLM."""
        return "together"

    def __call__(
        self,
        prompt: str,
        **kkwargs: Any,
    ) -> str:
        """Call to Together endpoint."""
        
        together.api_key = self.api_key
        output = together.Complete.create(
            get_prompt(prompt),
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        # text = output['output']['choices'][0]['text']
        
        return output['output']['choices'][0]['text']

if __name__ == "__main__":
    try:
        assistant = TogetherLLM()
        while True:
            response = assistant(input('\n[Prompt]# '))
            print(response)
    except KeyboardInterrupt:
        sys.exit(1)