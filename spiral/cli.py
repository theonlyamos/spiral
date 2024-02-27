import sys
import logging
import argparse
from argparse import Namespace

from spiral.llms import (
    Coral, 
    load_llm,
    list_llms
)

from .agents import AIAssistant
from .tools import (
    Calculator, YoutubePlayer,
    WorldNews, PythonREPL,
    FSBrowser, SearchTool,
    InternetBrowser, tool
)

from .config import VERSION

def start(args: Namespace):
    try:
        if args.models:
            print(list_llms())
            sys.exit()
        llm = None
        if args.llm:
            llm = load_llm(args.llm)
        llm = llm() if llm else Coral()
        # llm = TogetherLLM()
        assistant = AIAssistant(llm=llm, name=args.name, verbose=args.verbose)
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

    parser.add_argument('--name', default='Adam', help='Set name of agent')
    parser.add_argument('--llm', default='', help='Set llm to use')
    parser.add_argument('--api-key', default='', help='Set api key of selected llm')
    parser.add_argument('--models', action='store_true', help='Get a list of all supported models')
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
