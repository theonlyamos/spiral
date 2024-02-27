import sys
import json
import asyncio
import logging
from typing import Optional, List, Dict, Union
from pydantic import BaseModel, Field

from ..llms.base import LLM
from ..tools.base import Tool
from ..agents.templates import PROMPT_TEMPLATE

logging.basicConfig(
    format='%(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    level=logging.INFO
)
logger = logging.getLogger('spiral.log')

class Agent(BaseModel):
    """
    Base Agent Class
    """
    
    name: str = Field(default='Avatar')
    
    llm: LLM
    """Selected llm to use for agent"""
    
    tools: List[Tool] = Field(default=[])
    """Tools to be used by agent"""
    
    memory: List[Dict[str, str]] = []
    
    prompt_template: str = Field(default=PROMPT_TEMPLATE)
    """Base system prompt template"""
    
    verbose: bool = Field(default=False)
    """Verbose mode flag"""
    
    def generate_prompt(self, query: str)->dict:
        """Generates a prompt from a query and a dictionary of tools.

        Args:
        query: A string containing the query.

        Returns:
        A string containing the generated prompt.
        """

        tools_str = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        available_tools = [tool.name for tool in self.tools]
        
        prompt = self.prompt_template
        prompt = prompt.replace("{name}", self.name)
        # prompt = prompt.replace("{query}", query)
        prompt = prompt.replace("{tools}", tools_str)
        prompt = prompt.replace("{available_tools}", json.dumps(available_tools))

        self.memory.append({'User': query})
        
        for line in self.memory:
            for key, value in line.items():
                prompt += f'\n\n{key}: {value}'

        return {
            'type': 'query',
            'user_name': 'User',
            'output': prompt,
            'is_final': False
        }
    
    def get_tool_by_name(self, name: str)-> Optional[Tool]:
        for tool in self.tools:
            if tool.name.lower() == name.lower():
                return tool
        return None
    
    def process_response(self, response: str)-> Union[dict, str]:
        response = response.strip()
        response_data = response
        try:
            if response.startswith('{') or response.startswith('```json'):
                if response.startswith('```json'):
                    response = "\n".join(response.splitlines()[1:-1]).replace("\\", "\\\\")
                cb_last_index = response.rindex('}')
                cleaned_response = response[:cb_last_index+1]
                # cleaned_response = cleaned_response.replace("\n", "\\n")
                response_data = json.loads(cleaned_response)
                
                final_result_keys = ['final_answer', 'function_call_result']
                
                if response_data['type'] in final_result_keys:
                    return response_data['result']
                tool = self.get_tool_by_name(response_data['function'])
                
                if not tool:
                    raise Exception(f'Tool {response_data["function"]} not found')
                
                if self.verbose:
                    logger.info(f"Running function '{tool.name}' with parameters: {response_data['arguments']}")
                if isinstance(response_data['arguments'], list):
                    result = tool.run(*response_data['arguments'])
                else:
                    result = tool.run(response_data['arguments'])
                
                response_json = {}
                response_json['type'] = 'function_call_result'
                response_json['result'] = result
                
                return response_json
            else:
                raise Exception('Not a json object')
        except Exception as e:
            # logger.warning(str(e))
            return response_data
    
    # def generate_response(self, response: str)->dict:
    #     """_summary_

    #     Args:
    #         response (str): _description_

    #     Returns:
    #         str: _description_
    #     """
        
    #     self.memory.append({'AI Assistant': response})

    #     try:
    #         result = {}
    #         response = response.strip()
    #         for line in response.splitlines():
    #             r_line = line.split(":")
    #             if len(r_line) > 1:
    #                 r_key = r_line[0].strip().rstrip('"').lstrip('"').rstrip("'").lstrip("'")
    #                 r_value = r_line[1].strip().rstrip('"').lstrip('"').rstrip("'").lstrip("'").rstrip(",").rstrip('"')
    #                 result[r_key] = r_value

    #         if result['action']:
    #             action_tool = self.get_tool_by_name(result['action'])
    #             if action_tool:
    #                 tool = action_tool['execute']
    #                 if result['action_input']:
    #                     output = tool(result['action_input'])
    #                 else:
    #                     output= tool()
                    
    #                 return {
    #                     'type': 'tool_usage',
    #                     'user_name': result['action'],
    #                     'output': f"The answer from {result['action']} is {output}",
    #                     'is_final': False
    #                 }
    #         return {
    #             'type': 'response',
    #             'user_name': 'ChatBot',
    #             'output': result['final_answer'],
    #             'is_final': True
    #         }
    #     except Exception as e:
    #         logger.exception(str(e))
    #         return {
    #             'type': 'response',
    #             'user_name': 'ChatBot',
    #             'output': str(e),
    #             'is_final': True
    #         }
    
    def add_tool(self, tool: Tool):
        """Adds an additional tool to this LLM object"""
        self.tools.append(tool)
    
    async def handle_request(self, request):
        tool_name = request["tool_name"]
        params = request["params"]

        if hasattr(self, tool_name):
            tool = getattr(self, tool_name)

            if callable(tool):
                return await self.call_tool(tool, params)
            else:
                raise ValueError(f"{tool_name} is not a callable tool")
        else:
            raise ValueError(f"tool {tool_name} not found")

    async def call_tool(self, tool, params):
        if asyncio.iscoroutinefunction(tool):
            return await tool(**params)
        else:
            return tool(**params)
    
    async def initialize(self):
        """
        Initialize the llm
        """
        query = input("\nUser (q to quit): ")
        while query:
            try:
                if query in ['q', 'quit']:
                    print('Exiting...')
                    sys.exit(1)
                
                full_prompt = self.generate_prompt(query)
                # print(full_prompt['output'])
                response = self.llm(full_prompt['output']) # type: ignore
                if self.verbose:
                    print(response)
                self.memory.append({'AI Assistant': response})
                
                result = self.process_response(response)

                if isinstance(result, dict) and result['type'] == 'function_call_result':
                    query = json.dumps(result)
                else:
                    print(f"\n{self.name}: {result}")
                    query = input("\nUser (q to quit): ")
                    
            except KeyboardInterrupt:
                print('Exiting...')
                sys.exit(1)
            except Exception as e:
                print(str(e))

    def start(self):
        """
        Initialize agent
        """
        task = asyncio.run(self.initialize())

        return task