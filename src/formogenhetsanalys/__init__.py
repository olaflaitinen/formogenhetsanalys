"""Förmögenhetsanalys: graph-aware estimation of wealth concentration in Sweden."""

from formogenhetsanalys._version import __version__
from formogenhetsanalys.config import Config
from formogenhetsanalys.pipelines.runner import Pipeline
from formogenhetsanalys.seeds import set_global_seed

__author__ = "Gustav Olaf Yunus Laitinen-Fredriksson Lundström Imanov"
__license__ = "EUPL-1.2"

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "Config",
    "Pipeline",
    "set_global_seed",
]
