import sys
import json
import asyncio
import logging
from typing import Optional, List, Dict, Union
from pydantic import BaseModel, Field

from ..llms.base import LLM
from ..tools.base import Tool
from ..tasks.base import Task
from ..llms.actions import load_llm, list_llms
from ..agents.templates import PROMPT_TEMPLATE

logging.basicConfig(
    format='%(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    level=logging.WARNING
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
    
    sub_agents: List['Agent'] = Field(default=[])
    """Sub agents that can be called by this agent"""
    
    task: Optional[Task] = None
    """Current task assigned to the agent"""
    
    is_sub_agent:  bool = Field(default=False)
    """Flag indicating if agent is a sub agent"""
    
    system_prompt: str = Field(default="")
    """System prompt for context"""
    
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
        
        self.system_prompt = prompt
        
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
    
    def add_sub_agent(self, agent: 'Agent'):
        """Adds a sub agent to the list of sub agents"""
        self.sub_agents.append(agent)
    
    def get_tool_by_name(self, name: str)-> Optional[Tool]:
        for tool in self.tools:
            if tool.name.lower() == name.lower():
                return tool
        return None
    
    def process_response(self, response: str)-> Union[dict, str]:
        response = response.strip()
        # response = response.replace("\\", "\\\\")
        response_data = self.extract_json(response)
        
        try:
            if isinstance(response_data, dict):
                final_result_keys = ['final_answer', 'function_call_result']
                
                if response_data['type'].replace('\\', '') in final_result_keys: # type: ignore
                    return response_data['result'] # type: ignore
                tool = self.get_tool_by_name(response_data['function']) # type: ignore
                
                if not tool:
                    raise Exception(f'Tool {response_data["function"]} not found') # type: ignore
                
                if self.verbose:
                    logger.info(f"Running function '{tool.name}' with parameters: {response_data['arguments']}") # type: ignore
                if isinstance(response_data['arguments'], list): # type: ignore
                    result = tool.run(*response_data['arguments']) # type: ignore
                else:
                    result = tool.run(response_data['arguments']) # type: ignore
                
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
    
    def extract_json(self, content: str) -> dict | str:
        """Extract json content from response string

        Args:
            content (str): The response string to extract json from

        Returns:
            dict|str: Result of the extraction
        """
        try:
            # Find the start and end index of the JSON string
            start_index = content.find('{')
            end_index = content.find('}', start_index) + 1
            
            # Extract the JSON string
            json_str = content[start_index:end_index]
            
            # Convert the JSON string to a Python dictionary
            json_dict = json.loads(json_str)
            
            return json_dict
        except Exception as e:
            logger.warning(str(e))
            return content
    
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
                if query.lower() in ['q', 'quit', 'exit']:
                    print('Exiting...')
                    sys.exit(1)
                elif query.lower() == 'add agent':
                    agent_name = input("\n[Enter agent name]: ")
                    agent_task = input("\n[Enter brief description of agent task]: ")
                    llms = list_llms()
                    llms_str = "\nAvailable LLMs:"
                    for index, llm in enumerate(llms):
                        llms_str += (f"\n[{index}] {llm}")
                    print(llms_str)
                    agent_llm = int(input("\n[Select LLM]: "))
                    selected_llm = llms[agent_llm]
                    llm = load_llm(selected_llm)
                    new_agent = Agent.create_agent(agent_name, llm(), agent_task) # type: ignore
                    self.add_sub_agent(new_agent)
                    print(f"\nAgent {agent_name} added successfully!")
                    
                    query = input("\nUser (q to quit): ")
                    continue
                elif query.lower() == 'list agents':
                    agents_str = "\nAvailable Agents:"
                    for index, agent in enumerate(self.sub_agents):
                        agents_str += (f"\n[{index}] {agent.name}")
                    print(agents_str)
                    query = input("\nUser (q to quit): ")
                    continue
                
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
    
    @classmethod
    def create_agent(cls, name: str, llm: LLM, task_description: str, tools: List[Tool] = [], is_sub_agent: bool = True):
        """Create a new sub -agent instance

        Args:
            name (str): Name of the agent
            llm (LLM): LLM instance
            task (Task): Task instance
            tools (List[Tool], optional): List of tools available to the agent. Defaults to [].
            is_sub_agent (bool, optional): Set whether agent is a sub_agent. Defaults to True.
        """
        task = Task(description=task_description)
        return cls(name=name, llm=llm,task=task, tools=tools, is_sub_agent=is_sub_agent)