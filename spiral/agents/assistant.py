from pydantic import Field
from ..agents.base import Agent
from ..agents.templates import ASSISTANT_TEMPLATE

class AIAssistant(Agent):
    """_summary_

    Args:
        Agent (_type_): _description_
    """
    PROMPT_TEMPLATE: str = Field(default=ASSISTANT_TEMPLATE)