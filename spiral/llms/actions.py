import inspect
import importlib
from ..llms import LLM
from pathlib import Path
import logging
import sys

def load_llm(model_name: str):
    """Dynamically load LLMs based on name"""
    try:
        model_name = model_name.lower()
        module_path = Path(__file__, '..').resolve()
        sys.path.append(str(module_path))
        module = __import__(str(inspect.getmodulename(Path('__init__.py'))))
        llm: type[LLM] = [f[1] for f in inspect.getmembers(module, inspect.isclass) if f[0].lower() == model_name][0]
        return llm
    except Exception as e:
        logging.error(str(e))
        return None
    
def list_llms():
    """List all supported LLMs"""
    try:
        module_path = Path(__file__, '..').resolve()
        sys.path.append(str(module_path))
        module = __import__(str(inspect.getmodulename(Path('__init__.py'))))
        return [f[0] for f in inspect.getmembers(module, inspect.isclass) if f[0] != 'LLM']
    except Exception as e:
        logging.error(str(e))
        return []