from pydantic import Field
from ..agents.base import Agent
from ..agents.templates import AUTONOMOUSE_AGENT

class AIAssistant(Agent):
    """_summary_

    Args:
        Agent (_type_): _description_
    """
    prompt_template: str = Field(default=AUTONOMOUSE_AGENT)