"""
central_das_emendas_teste
-------------------------
Função pública: load_csv()
"""
from importlib.metadata import version as _v
from .data_loader import load_csv

__all__ = ["load_csv"]
__version__ = _v(__package__ or "central_das_emendas_teste")
