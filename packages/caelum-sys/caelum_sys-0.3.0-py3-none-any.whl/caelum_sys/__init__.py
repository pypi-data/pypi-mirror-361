"""CaelumSys - Human-friendly system automation toolkit"""

from .auto_import_plugins import load_all_plugins
from .core_actions import do
from .registry import get_registered_command_phrases

# Auto-load all plugins when package is imported (quiet mode)
load_all_plugins(verbose=False)

__version__ = "0.3.0"
__author__ = "Joshua Wells"
__description__ = "System automation toolkit with 117+ commands across 16 plugins"

__all__ = ["do", "get_registered_command_phrases"]
