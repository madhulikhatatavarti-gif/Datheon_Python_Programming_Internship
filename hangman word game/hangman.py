#!/usr/bin/env python3
"""Terminal Hangman with ASCII gallows art.

- Picks a random secret word (from words.txt if present, otherwise a built-in list).
- 6 incorrect guesses allowed.
- Repeated guesses are reported and never cost an attempt.
"""

import os
import random

MAX_MISTAKES = 6
WORDS_FILE = "words.txt"  # optional: the google-10000-english word list

FALLBACK_WORDS = [
    "python", "keyboard", "network", "program", "variable", "function",
    "algorithm", "database", "compiler", "internet", "software", "hardware",
    "developer", "terminal", "library", "package", "protocol", "security",
    "machine", "learning", "gallows", "journey", "mountain", "elephant",
    "umbrella", "chocolate", "festival", "treasure", "dolphin", "lantern",
]

STAGES = [
    # 0 mistakes
    """
      +---+
      |   |
          |
          |
          |
          |
    =========
    """,
    # 1 mistake
    """
      +---+
      |   |
      O   |
          |
          |
          |
    =========
    """,
    # 2 mistakes
    """
      +---+
      |   |
      O   |
      |   |
          |
          |
    =========
    """,
    # 3 mistakes
    """
      +---+
      |   |
      O   |
     /|   |
          |
          |
    =========
    """,
    # 4 mistakes
    """
      +---+
      |   |
      O   |
     /|\\  |
          |
          |
    =========
    """,
    # 5 mistakes
    """
      +---+
      |   |
      O   |
     /|\\  |
     /    |
          |
    =========
    """,
    # 6 mistakes
    """
      +---+
      |   |
      O   |
     /|\\  |
     / \\  |
          |
    =========
    """,
]


def load_words():
    """Load words from words.txt (next to this script) if available."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), WORDS_FILE)
    if os.path.isfile(path):
        try:
            with open(path, encoding="utf-8") as f:
                words = [w.strip().lower() for w in f]
            words = [w for w in words if w.isalpha() and len(w) >= 4]
            if words:
                return words
        except OSError:
            pass
    return FALLBACK_WORDS


def masked(word, guessed):
    return " ".join(ch.upper() if ch in guessed else "_" for ch in word)


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def draw(word, guessed, mistakes, message=""):
    clear()
    print("=" * 36)
    print("            H A N G M A N")
    print("=" * 36)
    print(STAGES[mistakes])
    print(f"  Word:   {masked(word, guessed)}\n")
    wrong = sorted(g for g in guessed if g not in word)
    right = sorted(g for g in guessed if g in word)
    print(f"  Wrong letters:   {' '.join(w.upper() for w in wrong) or '-'}")
    print(f"  Correct letters: {' '.join(r.upper() for r in right) or '-'}")
    print(f"  Attempts left:   {MAX_MISTAKES - mistakes} / {MAX_MISTAKES}")
    if message:
        print(f"\n  >> {message}")
    print()


def play(words):
    word = random.choice(words)
    guessed = set()
    mistakes = 0
    message = "Guess a letter!"

    while mistakes < MAX_MISTAKES and not set(word) <= guessed:
        draw(word, guessed, mistakes, message)
        guess = input("  Your guess: ").strip().lower()

        if len(guess) != 1 or not guess.isalpha():
            message = "Please enter a single letter (A-Z)."
        elif guess in guessed:
            message = f"You already guessed '{guess.upper()}'. No penalty - try another!"
        else:
            guessed.add(guess)
            if guess in word:
                message = f"Nice! '{guess.upper()}' is in the word."
            else:
                mistakes += 1
                message = f"Sorry, '{guess.upper()}' is not in the word."

    draw(word, guessed, mistakes)
    if set(word) <= guessed:
        print("  *************************************")
        print("  *          YOU WIN!  \\o/            *")
        print("  *************************************")
        print(f"  You saved him! The word was: {word.upper()}")
    else:
        print("  -------------------------------------")
        print("  |          GAME OVER  x_x           |")
        print("  -------------------------------------")
        print(f"  You ran out of attempts. The word was: {word.upper()}")
    print()


def main():
    words = load_words()
    while True:
        play(words)
        again = input("  Play again? (y/n): ").strip().lower()
        if again not in ("y", "yes"):
            print("\n  Thanks for playing. Goodbye!\n")
            break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\n  Game interrupted. Goodbye!\n")
