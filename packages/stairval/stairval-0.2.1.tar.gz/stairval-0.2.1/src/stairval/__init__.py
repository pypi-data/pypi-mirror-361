"""
Stairval is a framework for validating hierarchical data structures.
"""

from ._api import Level, Issue
from ._auditor import Auditor, ITEM

__version__ = "0.2.1"

__all__ = [
    "Auditor",
    "Issue",
    "Level",
    "ITEM",
]
