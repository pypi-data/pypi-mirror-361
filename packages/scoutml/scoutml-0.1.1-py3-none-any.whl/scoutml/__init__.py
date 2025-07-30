"""
ScoutML - Scout ML Research Papers

A powerful command-line interface for discovering, analyzing, and implementing ML research.
"""

__version__ = "0.1.0"
__author__ = "ProspectML"
__email__ = "info@prospectml.com"

from .client import ScoutMLClient
from .config import Config

__all__ = ["ScoutMLClient", "Config"]