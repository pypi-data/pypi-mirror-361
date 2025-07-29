"""
pyCCMM - Python implementation of CCMM (Czech Core Metadata Model) standard.

This package provides classes and utilities for working with CCMM metadata,
including validation, XML generation, and data model definitions.
"""

from .ccmm_models import *
from .ccmm_handler import CCMMHandler
from .ccmm_metadata_handler import CCMMMetadataHandler

__version__ = "1.0.0"
__author__ = "Roman Dvořák, Institute of Physics, Czech Academy of Sciences"
__email__ = "romandvorak@mlab.cz"

__all__ = [
    'CCMMHandler',
    'CCMMMetadataHandler',
    # Export all models
    'Dataset',
    'Title',
    'Identifier',
    'Subject',
    'Description',
    'Agent',
    'QualifiedRelation',
    'TimeReference',
    'Location',
    'Distribution',
    'MetadataRecord',
    # Export all enums
    'AgentType',
    'RoleType',
    'TimeReferenceType',
    'DistributionType',
    'IdentifierScheme',
    'LanguageCode',
]
