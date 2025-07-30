"""
Utility functions for loading and saving LSS files.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Union

from .models import Run
from .parser import LSSParser
from .serializer import LSSSerializer


def load_lss_file(file_path: Union[str, Path]) -> Run:
    """
    Load and parse an LSS file.
    
    Args:
        file_path: Path to the .lss file
        
    Returns:
        Run object containing parsed data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ET.ParseError: If the XML is malformed
        ValueError: If the file is not a valid LSS file
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not file_path.suffix.lower() == '.lss':
        raise ValueError(f"File must have .lss extension: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        xml_content = f.read()
    
    return LSSParser.parse_xml(xml_content)


def save_lss_file(run: Run, file_path: Union[str, Path], pretty: bool = True) -> None:
    """
    Save a Run object to an LSS file.
    
    Args:
        run: Run object to save
        file_path: Path where to save the .lss file
        pretty: Whether to format the XML with pretty printing
        
    Raises:
        ValueError: If the file path is invalid
    """
    file_path = Path(file_path)
    
    if not file_path.suffix.lower() == '.lss':
        raise ValueError(f"File must have .lss extension: {file_path}")
    
    # Create directory if it doesn't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    if pretty:
        xml_content = LSSSerializer.serialize_to_pretty_xml(run)
    else:
        xml_content = LSSSerializer.serialize_to_xml(run)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(xml_content) 