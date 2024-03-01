import sys
import logging
import argparse
from argparse import Namespace

from spiral.llms import (
    Cohere, OpenAI,
    load_llm,
    list_llms
)

from .agents import AIAssistant, Agent
from .tools import (
    Calculator, YoutubePlayer,
    WorldNews, PythonREPL,
    FSBrowser, SearchTool,
    InternetBrowser, tool
)

from .config import VERSION

def manage_agents(args: Namespace):
    try:
        if args.add:
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
            new_agent = Agent.create_agent(agent_name, llm(), agent_task, is_sub_agent=False) # type: ignore
            print(f"\nAgent {new_agent.name} added successfully!")
        elif args.list:
            agents_str = "\nAvailable Agents:"
            for index, agent in enumerate(Agent.list_agents()):
                agents_str += (f"\n[{index}] {agent.name}")                 #type: ignore
            print(agents_str)
    except KeyboardInterrupt:
        print()
        sys.exit()
    except Exception as e:
        logging.warning(str(e))
        sys.exit(1)

def start(args: Namespace):
    try:
        if args.platforms:
            print("\nAvailable Platforms:")
            for index, l in enumerate(list_llms()):
                print(f"[{index}] {l}")
            sys.exit()
        platform = None
        if args.platform:
            platform = load_llm(model_name=args.platform)
        platform = platform() if platform else Cohere()
        
        if args.api_key:
            platform.api_key = args.api_key
        if args.model:
            platform.model = args.model
        
        platform.temperature = args.temperature
        # llm = TogetherLLM()
        assistant = AIAssistant(llm=platform, name=args.name, verbose=args.verbose)
        
        assistant.add_tool(Calculator())
        assistant.add_tool(YoutubePlayer())
        assistant.add_tool(WorldNews())
        assistant.add_tool(FSBrowser())
        assistant.add_tool(PythonREPL())
        assistant.add_tool(InternetBrowser())
        assistant.add_tool(SearchTool())
        assistant.start()
    except Exception as e:
        logging.error(str(e))
        parser.print_help()
        sys.exit(1)

def get_arguments():
    global parser
    
    subparsers = parser.add_subparsers()
    agents_parser = subparsers.add_parser('agents', help="Manage agents")
    agents_parser.add_argument("name", type=str, nargs="?", help="Name of an agent to manage (details|update|remove)")  
    agents_parser.add_argument('--list', action='store_true', help='List all saved agents')
    agents_parser.add_argument('--add', action='store_true', help='Create a new agent')
    agents_parser.add_argument('--update', action='store_true', help='Update an agent')
    agents_parser.add_argument('--remove', action='store_true', help='Delete an agent')
    agents_parser.set_defaults(func=manage_agents)

    parser.add_argument('--name', type=str, default='Adam', help='Set name of agent')
    parser.add_argument('--platform', default='', help='Set llm platform to use')
    parser.add_argument('--platforms', action='store_true', help='Get a list of all supported platforms')
    parser.add_argument('--model', type=str, default='', help='Specify model or model_url to use')
    parser.add_argument('--api-key', type=str, default='', help='Set api key of selected llm')
    parser.add_argument('--temperature', type=float, default=0.1, help='Set temperature of model')
    parser.add_argument('--verbose', action='store_true', help='Set verbose mode')
    parser.add_argument('-v','--version', action='version', version=f'%(prog)s {VERSION}')
    parser.set_defaults(func=start)
    return parser.parse_args()

def main():
    global parser
    try:
        parser = argparse.ArgumentParser(description="Build and run ai agents on your computer")
        args = get_arguments()
        args.func(args)

    except Exception as e:
        logging.error(str(e))
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
