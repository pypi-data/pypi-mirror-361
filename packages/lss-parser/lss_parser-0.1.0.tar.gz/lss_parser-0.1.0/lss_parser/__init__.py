"""
LiveSplit LSS File Parser

A Python module for parsing and manipulating LiveSplit .lss files.
Converts XML structure to Python objects for easy manipulation.
"""

try:
    from pydantic import BaseModel
except ImportError:
    raise ImportError("Pydantic is required for this module. Install with: pip install pydantic")

# Import models
from .models import (Attempt, AutoSplitterSettings, Metadata, Run, Segment,
                     SegmentTime, SplitTime, Time)
# Import parser and serializer
from .parser import LSSParser
from .serializer import LSSSerializer
# Import utility functions
from .utils import load_lss_file, save_lss_file

# Version info
__version__ = "0.1.0"
__author__ = "LSS Parser Team"
__description__ = "A Python module for parsing and manipulating LiveSplit .lss files"

# Public API
__all__ = [
    # Models
    "Time",
    "SplitTime",
    "SegmentTime",
    "Segment",
    "Attempt",
    "Metadata",
    "AutoSplitterSettings",
    "Run",
    # Parser and Serializer
    "LSSParser",
    "LSSSerializer",
    # Utility functions
    "load_lss_file",
    "save_lss_file",
    # Version info
    "__version__",
    "__author__",
    "__description__",
] 