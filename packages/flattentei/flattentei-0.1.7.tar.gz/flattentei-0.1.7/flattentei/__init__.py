"""
This module provides utilities to transform tei.xml files into a flat json format.
the format called flattei is json file where annotations and the text is separated.
(Standoff annotations)
"""

from . import tei_to_text_and_standoff
from . import loader
from .extract_parts import _get_units as get_units
from .extract_parts import get_units
from . import flatten_tei_folder
from .loader import FlatTeiLoader
from . import extract_parts
__all__ = ["tei_to_text_and_standoff", "get_units","loader", "flatten_tei_folder", "FlatTeiLoader", "extract_parts"]
