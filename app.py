from llms import TogetherLLM
from llms import Choral
from agents import AIAssistant
from tools import (
    Calculator, YoutubePlayer,
    WorldNews, FSBrowser,
    InternetBrowser
)

if __name__ == "__main__":
    # llm = Choral()
    llm = TogetherLLM()
    assistant = AIAssistant(llm=llm, name='Adam')
    assistant.add_tool(Calculator())
    assistant.add_tool(YoutubePlayer())
    assistant.add_tool(WorldNews())
    assistant.add_tool(FSBrowser())
    assistant.add_tool(InternetBrowser())
    assistant.start()