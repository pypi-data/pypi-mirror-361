"""
Toulouse - High-Performance Card Game Library for Reinforcement Learning

A modern, high-performance card library for RL/MCTS applications.
"""

from .core import (
    Card,
    Deck,
    get_card,
    get_card_system,
    register_card_system,
)

__version__ = "1.0.0"
__all__ = [
    "Card",
    "Deck", 
    "get_card",
    "get_card_system",
    "register_card_system",
] 