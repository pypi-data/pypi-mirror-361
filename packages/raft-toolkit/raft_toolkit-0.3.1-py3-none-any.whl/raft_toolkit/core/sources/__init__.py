"""
Input source providers for RAFT Toolkit.

This module provides an extensible system for handling different input sources
including local files, S3 buckets, and SharePoint sites.
"""

from .base import BaseInputSource, InputSourceConfig, SourceDocument, SourceValidationError
from .factory import InputSourceFactory
from .local import LocalInputSource
from .s3 import S3InputSource
from .sharepoint import SharePointInputSource

__all__ = [
    "BaseInputSource",
    "InputSourceConfig",
    "SourceDocument",
    "SourceValidationError",
    "LocalInputSource",
    "S3InputSource",
    "SharePointInputSource",
    "InputSourceFactory",
]
