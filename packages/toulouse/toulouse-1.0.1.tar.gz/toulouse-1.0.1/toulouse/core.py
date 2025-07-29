"""
Toulouse - High-Performance Card Game Library for Reinforcement Learning

A modern, high-performance card library for RL/MCTS applications.
- Uses dataclasses for Card (no Pydantic)
- Object pooling for Card instances
- O(1) set-based search in Deck
- Cached numpy state generation
- Lazy loading of card names by language
- LRU cache for card system configs
- Pre-allocated numpy buffers for state vectors

Usage:
    from toulouse import Card, Deck, get_card
    deck = Deck.new_deck()
    card = get_card(value=1, suit=0)
    if deck.contains(card):
        deck.remove(card)
    state = deck.state
"""

import random
import numpy as np
from typing import Any, Iterator, Optional, Dict, List, Set
from dataclasses import dataclass, field
from functools import lru_cache
import weakref

_CARD_SYSTEMS: Dict[str, Dict[str, Any]] = {}

_CARD_SYSTEMS["italian_40"] = {
    "suits": ["Denari", "Coppe", "Spade", "Bastoni"],
    "values": list(range(1, 11)),
    "deck_size": 40,
    "_names": None,
}

_CARD_SYSTEMS["spanish_40"] = {
    "suits": ["Oros", "Copas", "Espadas", "Bastos"],
    "values": list(range(1, 11)),
    "deck_size": 40,
    "_names": None,
}

_NAMES_CACHE: Dict[str, Dict[int, str]] = {}


def _load_names_for_system(system_key: str, language: str) -> Dict[int, str]:
    cache_key = f"{system_key}_{language}"
    if cache_key not in _NAMES_CACHE:
        if system_key == "italian_40":
            if language == "en":
                _NAMES_CACHE[cache_key] = {
                    1: "Ace",
                    2: "Two",
                    3: "Three",
                    4: "Four",
                    5: "Five",
                    6: "Six",
                    7: "Seven",
                    8: "Jack",
                    9: "Knight",
                    10: "King",
                }
            elif language == "it":
                _NAMES_CACHE[cache_key] = {
                    1: "Asso",
                    2: "Due",
                    3: "Tre",
                    4: "Quattro",
                    5: "Cinque",
                    6: "Sei",
                    7: "Sette",
                    8: "Fante",
                    9: "Cavallo",
                    10: "Re",
                }
        elif system_key == "spanish_40":
            if language == "es":
                _NAMES_CACHE[cache_key] = {
                    1: "As",
                    2: "Dos",
                    3: "Tres",
                    4: "Cuatro",
                    5: "Cinco",
                    6: "Seis",
                    7: "Siete",
                    8: "Sota",
                    9: "Caballo",
                    10: "Rey",
                }
    return _NAMES_CACHE.get(cache_key, {})


@lru_cache(maxsize=32)
def get_card_system(key: str) -> Dict[str, Any]:
    if key not in _CARD_SYSTEMS:
        raise KeyError(f"Card system '{key}' is not registered.")
    return _CARD_SYSTEMS[key]


def register_card_system(key: str, config: Dict[str, Any]):
    if key in _CARD_SYSTEMS:
        raise ValueError(f"Card system '{key}' already exists!")
    for req in ["suits", "values", "deck_size"]:
        if req not in config:
            raise ValueError(f"Missing '{req}' in card system config.")
    _CARD_SYSTEMS[key] = config.copy()


_CARD_POOL: Dict[tuple, "Card"] = {}
_CARD_POOL_CLEANUP = weakref.WeakSet()


def get_card(value: int, suit: int, card_system_key: str = "italian_40") -> "Card":
    key = (value, suit, card_system_key)
    if key not in _CARD_POOL:
        _CARD_POOL[key] = Card(value=value, suit=suit, card_system_key=card_system_key)
        _CARD_POOL_CLEANUP.add(_CARD_POOL[key])
    return _CARD_POOL[key]


@dataclass(frozen=True)
class Card:
    value: int
    suit: int
    card_system_key: str = "italian_40"

    def __post_init__(self):
        system = get_card_system(self.card_system_key)
        if self.value not in system["values"]:
            raise ValueError(
                f"Value {self.value} not in allowed values: {system['values']}"
            )
        if not (0 <= self.suit < len(system["suits"])):
            raise ValueError(
                f"Suit {self.suit} out of range for system suits: {system['suits']}"
            )

    def to_index(self) -> int:
        system = get_card_system(self.card_system_key)
        idx = self.suit * len(system["values"]) + (self.value - min(system["values"]))
        return idx

    @property
    def state(self) -> np.ndarray:
        system = get_card_system(self.card_system_key)
        arr = np.zeros(system["deck_size"], dtype=np.uint8)
        arr[self.to_index()] = 1
        return arr

    def __str__(self) -> str:
        system = get_card_system(self.card_system_key)
        names = _load_names_for_system(self.card_system_key, "en")
        value_str = names.get(self.value, str(self.value))
        suit_str = system["suits"][self.suit]
        return f"{value_str} of {suit_str}"

    def __repr__(self) -> str:
        return f"Card(value={self.value}, suit={self.suit})"


@dataclass
class Deck:
    card_system_key: str = "italian_40"
    language: str = "en"
    _cards: List[Card] = field(default_factory=list)
    _card_set: Set[Card] = field(default_factory=set)
    _state_cache: Optional[np.ndarray] = None
    _state_dirty: bool = True
    _deck_size: int = 40

    def __post_init__(self):
        system = get_card_system(self.card_system_key)
        self._deck_size = system["deck_size"]
        if self._cards:
            self._card_set = set(self._cards)

    def __len__(self) -> int:
        return len(self._cards)

    def __iter__(self) -> Iterator[Card]:
        return iter(self._cards)

    def __getitem__(self, idx):
        return self._cards[idx]

    def __str__(self) -> str:
        return f"Deck of {len(self._cards)} cards ({self.card_system_key})"

    def __repr__(self) -> str:
        preview = ", ".join([str(card) for card in self._cards[:4]])
        return f"Deck(cards=[{preview}, ...], system='{self.card_system_key}')"

    def pretty_print(self) -> str:
        system = get_card_system(self.card_system_key)
        lines = []
        for suit_idx, suit in enumerate(system["suits"]):
            suit_cards = [card for card in self._cards if card.suit == suit_idx]
            suit_str = ", ".join(str(card) for card in suit_cards)
            lines.append(f"{suit}: {suit_str}")
        return "\n".join(lines)

    def draw(self, n: int = 1) -> List[Card]:
        n = max(0, min(n, len(self._cards)))
        drawn = self._cards[:n]
        self._cards = self._cards[n:]
        for card in drawn:
            self._card_set.discard(card)
        self._state_dirty = True
        return drawn

    def shuffle(self):
        random.shuffle(self._cards)
        self._state_dirty = True

    def sort(self):
        self._cards.sort(key=lambda c: c.to_index())
        self._state_dirty = True

    def append(self, card: Card):
        if card.card_system_key != self.card_system_key:
            raise ValueError(
                f"Cannot add card from system '{card.card_system_key}' to '{self.card_system_key}' deck."
            )
        self._cards.append(card)
        self._card_set.add(card)
        self._state_dirty = True

    def remove(self, card: Card):
        self._cards.remove(card)
        self._card_set.discard(card)
        self._state_dirty = True

    def contains(self, card: Card) -> bool:
        return card in self._card_set

    def reset(self):
        system = get_card_system(self.card_system_key)
        self._cards = [
            get_card(value=v, suit=s, card_system_key=self.card_system_key)
            for s in range(len(system["suits"]))
            for v in system["values"]
        ]
        self._card_set = set(self._cards)
        self._state_dirty = True

    @property
    def state(self) -> np.ndarray:
        if self._state_dirty or self._state_cache is None:
            arr = np.zeros(self._deck_size, dtype=np.uint8)
            for card in self._cards:
                arr[card.to_index()] = 1
            self._state_cache = arr
            self._state_dirty = False
        return self._state_cache.copy()

    def move_card_to(self, card: Card, other_deck: "Deck"):
        self.remove(card)
        other_deck.append(card)

    @classmethod
    def new_deck(
        cls,
        card_system_key: str = "italian_40",
        language: str = "en",
        sorted_deck: bool = True,
    ) -> "Deck":
        deck = cls(card_system_key=card_system_key, language=language)
        deck.reset()
        if not sorted_deck:
            deck.shuffle()
        return deck

    @classmethod
    def from_cards(
        cls,
        cards: List[Card],
        card_system_key: str = "italian_40",
        language: str = "en",
    ) -> "Deck":
        deck = cls(card_system_key=card_system_key, language=language)
        deck._cards = list(cards)
        deck._card_set = set(cards)
        deck._state_dirty = True
        return deck
