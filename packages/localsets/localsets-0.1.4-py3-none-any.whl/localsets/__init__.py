"""
Pokemon Random Battle Data Package

A Python package providing offline access to Pokemon random battle data 
with automatic updates from the official source repository.
"""

__version__ = "0.1.0"
__author__ = "Pokemon RandBats Team"

from .core import PokemonData, RandBatsData
from .formats import (
    get_pokemon, update_data, list_pokemon,
    get_smogon_sets, list_smogon_pokemon
)

__all__ = [
    'PokemonData',
    'RandBatsData',
    'get_pokemon', 
    'update_data',
    'list_pokemon',
    'get_smogon_sets',
    'list_smogon_pokemon',
] 