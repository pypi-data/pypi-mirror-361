import pytest
import numpy as np
from toulouse import Card
import time
from toulouse import Deck, get_card


# --- Test valid card creation and core properties ---
def test_card_creation_valid():
    """Basic creation: check field assignments, index, and one-hot state."""
    card = Card(value=1, suit=0)
    assert card.value == 1
    assert card.suit == 0
    assert card.card_system_key == "italian_40"
    # Index should be 0 for Asso di Denari
    assert card.to_index() == 0
    # State vector: all zero except first
    arr = card.state
    assert isinstance(arr, np.ndarray)
    assert arr.sum() == 1
    assert arr[0] == 1
    assert arr.shape == (40,)


# --- Test string representation ---
def test_card_creation_str():
    """Check string representation."""
    card = Card(value=10, suit=2)
    assert str(card) == "King of Spade" or str(card) == "10 of Spade"
    card_it = Card(value=8, suit=1)
    assert str(card_it) == "Jack of Coppe" or str(card_it) == "8 of Coppe"
    card_es = Card(value=9, suit=3, card_system_key="spanish_40")
    assert str(card_es) == "Knight of Bastos" or str(card_es) == "9 of Bastos"


# --- Test __repr__, equality, hashability ---
def test_card_repr_and_hash():
    """Check __repr__, equality, and hashability (should behave like a value object)."""
    card1 = Card(value=7, suit=2)
    card2 = Card(value=7, suit=2)
    assert card1 == card2
    assert hash(card1) == hash(card2)
    r = repr(card1)
    assert "value=7" in r and "suit=2" in r


# --- Test creation with invalid value or suit ---
def test_card_creation_invalid_value():
    """Creating a card with an invalid value should raise ValueError."""
    with pytest.raises(ValueError):
        Card(value=99, suit=0)
    with pytest.raises(ValueError):
        Card(value=0, suit=1)


def test_card_creation_invalid_suit():
    """Creating a card with an invalid suit should raise ValueError."""
    with pytest.raises(ValueError):
        Card(value=2, suit=44)
    with pytest.raises(ValueError):
        Card(value=2, suit=-1)


# --- Test to_index covers all ---
def test_card_to_index_bounds():
    """to_index() covers all possible cards in the system (no duplicate/no miss)."""
    seen = set()
    for suit in range(4):
        for value in range(1, 11):
            card = Card(value=value, suit=suit)
            idx = card.to_index()
            assert 0 <= idx < 40
            assert idx not in seen, f"Duplicate index: {idx}"
            seen.add(idx)
    assert len(seen) == 40  # Must fill all slots


# --- Test state is always a one-hot ---
def test_card_state_is_onehot():
    """Card state is always a one-hot vector with one '1' at the card's index."""
    for suit in range(4):
        for value in range(1, 11):
            card = Card(value=value, suit=suit)
            arr = card.state
            assert arr.sum() == 1
            assert arr[card.to_index()] == 1
            assert arr.dtype == np.uint8


# --- Variant system (example) ---
def test_card_system_variants():
    """Test creating cards from another system (if available, e.g., spanish_40)."""
    try:
        card = Card(value=1, suit=0, card_system_key="spanish_40")
        assert str(card).startswith("As") or str(card).startswith("1")
        assert card.to_index() == 0
    except KeyError:
        pass  # System not present, skip


# --- Immutability ---


# --- Usage and Performance Demonstration ---


def test_performance_deck_creation():
    """Benchmark deck creation and reset."""
    t0 = time.perf_counter()
    for _ in range(1000):
        deck = Deck.new_deck()
    t1 = time.perf_counter()
    print(f"Deck creation (1000x): {t1-t0:.6f} seconds")
    assert (t1 - t0) < 1.0  # Should be very fast


def test_performance_shuffle_draw():
    """Benchmark shuffling and drawing cards."""
    deck = Deck.new_deck()
    t0 = time.perf_counter()
    for _ in range(1000):
        deck.shuffle()
        _ = deck.draw(5)
        deck.reset()
    t1 = time.perf_counter()
    print(f"Shuffle+draw+reset (1000x): {t1-t0:.6f} seconds")
    assert (t1 - t0) < 2.0


def test_performance_card_lookup():
    """Benchmark O(1) card lookup in deck."""
    deck = Deck.new_deck()
    card = get_card(5, 2)
    t0 = time.perf_counter()
    for _ in range(10000):
        _ = deck.contains(card)
    t1 = time.perf_counter()
    print(f"Card lookup (10000x): {t1-t0:.6f} seconds")
    assert (t1 - t0) < 0.5


def test_performance_state_vector():
    """Benchmark state vectorization for deck and card."""
    deck = Deck.new_deck()
    card = get_card(3, 1)
    t0 = time.perf_counter()
    for _ in range(10000):
        _ = deck.state
        _ = card.state
    t1 = time.perf_counter()
    print(f"State vectorization (deck+card, 10000x): {t1-t0:.6f} seconds")
    assert (t1 - t0) < 1.0
