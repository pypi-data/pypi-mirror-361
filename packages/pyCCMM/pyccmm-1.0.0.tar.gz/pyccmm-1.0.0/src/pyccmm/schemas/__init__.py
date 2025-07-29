"""
CCMM Schemas package

This package contains the CCMM (Cultural Collection Management Metadata) schemas
as a git submodule from the official CCMM repository.
"""

import os

def get_schema_path(schema_name: str = "dataset") -> str:
    """
    Get the path to a specific CCMM schema file.
    
    Args:
        schema_name: Name of the schema (default: "dataset")
        
    Returns:
        Path to the schema XSD file
    """
    schemas_dir = os.path.join(os.path.dirname(__file__), "CCMM")
    return os.path.join(schemas_dir, schema_name, "schema.xsd")

def get_ccmm_root() -> str:
    """
    Get the root path of the CCMM schemas directory.
    
    Returns:
        Path to the CCMM schemas root directory
    """
    return os.path.join(os.path.dirname(__file__), "CCMM")
