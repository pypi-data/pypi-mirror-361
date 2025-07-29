# ⚡ Toulouse: High-Performance Card Library for Machine Learning & Reinforcement Learning

Toulouse is a modern, lightning-fast Python library for representing, manipulating, and vectorizing card games—designed for the needs of the ML and RL community.

- 🚀 **Blazing Fast**: O(1) card lookup, object pooling, and pre-allocated numpy buffers
- 🧩 **Extensible**: Easily add new card systems (Italian, Spanish, custom...)
- 🧑‍💻 **ML/RL Ready**: One-hot numpy state vectors for cards and decks
- 🌍 **Multilingual**: Card names in multiple languages (EN, IT, ES)
- 🧪 **Tested & Typed**: Robust, well-typed, and ready for research or production

---

## Installation

```bash
pip install toulouse
```
or
```bash
uv add toulouse
```
---

## Quick Start

```python
from toulouse import Card, Deck, get_card

# Create a new Italian 40-card deck (sorted)
deck = Deck.new_deck(card_system_key="italian_40")
print(deck)  # Deck of 40 cards (italian_40)

# Draw a card
drawn = deck.draw(1)[0]
print(drawn)  # Ace of Denari

# Check if a card is in the deck
card = get_card(value=1, suit=0)  # Ace of Denari
print(deck.contains(card))  # False (if just drawn)

# Get the deck state as a numpy vector (for ML/RL)
print(deck.state.shape)  # (40,)

# Reset and shuffle the deck
deck.reset()
deck.shuffle()
```

---

## Supported Card Systems

- **italian_40**: Denari, Coppe, Spade, Bastoni
- **spanish_40**: Oros, Copas, Espadas, Bastos
- *Add your own system easily (see below)*

---

## API Reference

### Card

```python
from toulouse import Card, get_card

card = get_card(value=7, suit=2, card_system_key="italian_40")
print(card)           # Seven of Spade
print(card.to_index()) # Unique index in the deck
print(card.state)     # One-hot numpy array (length deck_size)
```

- `Card(value, suit, card_system_key="italian_40")`: Immutable, hashable card instance
- `.to_index()`: Returns unique index for the card in its system
- `.state`: One-hot numpy array (length = deck size)
- `__str__`, `__repr__`: Human-readable

### Deck

```python
from toulouse import Deck

deck = Deck.new_deck(card_system_key="spanish_40", sorted_deck=False)
print(len(deck))      # 40
hand = deck.draw(3)   # Draw 3 cards
print(deck.state)     # Numpy binary vector (remaining cards)
deck.append(hand[0])  # Add a card back
deck.shuffle()        # Shuffle the deck
deck.sort()           # Sort the deck
deck.reset()          # Restore to full deck
```

- `Deck.new_deck(card_system_key="italian_40", language="en", sorted_deck=True)`: Create a new deck
- `.draw(n)`: Draw n cards (removes from deck)
- `.append(card)`: Add a card
- `.remove(card)`: Remove a card
- `.contains(card)`: O(1) check for card presence
- `.reset()`: Restore to full deck
- `.shuffle()`, `.sort()`: Shuffle or sort
- `.state`: Numpy binary vector (length = deck size)
- `.pretty_print()`: Grouped by suit, human-readable
- `.move_card_to(card, other_deck)`: Move card between decks

### Card System Management

```python
from toulouse import register_card_system, get_card_system

my_system = {
    "suits": ["Red", "Blue"],
    "values": [1, 2, 3],
    "deck_size": 6,
}
register_card_system("mini_6", my_system)
print(get_card_system("mini_6"))
```

- `register_card_system(key, config)`: Add a new card system
- `get_card_system(key)`: Retrieve system config

---

## Machine Learning & RL Integration

- **Card state**: `card.state` is a one-hot numpy array (length = deck size)
- **Deck state**: `deck.state` is a binary numpy array (1 if card present)
- **Fast vectorization**: Pre-allocated, cached numpy buffers for speed

Example:

```python
from toulouse import Deck

deck = Deck.new_deck()
obs = deck.state  # Use as RL agent observation
```

---

## Performance

Toulouse is engineered for speed. Here are real benchmark results from the test suite (Apple Silicon, Python 3.11):

```
Deck creation (1000x): 0.0062 seconds
Shuffle+draw+reset (1000x): 0.0099 seconds
Card lookup (10000x): 0.0006 seconds
State vectorization (deck+card, 10000x): 0.0042 seconds
```

- Creating 1000 decks takes less than 7 milliseconds
- 10,000 card lookups in under 1 millisecond
- Deck and card state vectorization is nearly instantaneous

This makes Toulouse ideal for RL/ML environments where speed is critical.

---

## Extending Toulouse

Add new card systems for custom games:

```python
from toulouse import register_card_system, Deck

register_card_system("custom_8", {
    "suits": ["Alpha", "Beta"],
    "values": [1, 2, 3, 4],
    "deck_size": 8,
})
deck = Deck.new_deck(card_system_key="custom_8")
print(deck)
```

---

## Testing

Run the test suite with pytest:

```bash
pytest tests/
```

---

## License

MIT — Use, modify, and share freely.
