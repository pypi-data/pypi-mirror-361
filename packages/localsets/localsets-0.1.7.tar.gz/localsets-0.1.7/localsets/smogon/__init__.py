"""
Smogon competitive sets data module.

Provides access to Smogon competitive Pokemon sets data.
This data is bundled at build time and does not require runtime updates.
"""

from .sets import SmogonSets

__all__ = ['SmogonSets'] 