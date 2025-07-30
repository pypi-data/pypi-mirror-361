# expose ghn_jupyter_ai_magics ipython extension
# DO NOT REMOVE.
from ghn_jupyter_ai_magics import load_ipython_extension, unload_ipython_extension

# expose ghn_jupyter_ai_magics providers
# DO NOT REMOVE.
from ghn_jupyter_ai_magics.providers import *

from ._version import __version__
from .extension import AiExtension


def _jupyter_labextension_paths():
    return [{"src": "labextension", "dest": "@jupyter-ai/core"}]


def _jupyter_server_extension_points():
    return [{"module": "jupyter_ai", "app": AiExtension}]
