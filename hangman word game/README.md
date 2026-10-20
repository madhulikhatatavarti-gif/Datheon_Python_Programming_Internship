# Datheon Python Programming Internship

This repository contains my completed tasks for the Datheon Python Programming Internship.

## Task: Hangman (Terminal Game)

A terminal-based Hangman game written in Python 3 using only the standard library.

### Features

- Picks a random secret word with `random.choice()` from an English word list (`words.txt`).
- Shows the word as a masked string, for example `_ A _ H E _`.
- Tracks guessed letters in a set and lists correct and wrong letters.
- Allows 6 incorrect guesses, with ASCII gallows art that updates after each mistake.
- Repeated guesses show a message and do not cost an attempt.
- Rejects invalid input (numbers, symbols, or more than one letter).
- Separate victory and defeat screens, with an option to play again.

### Folder structure

```
hangman/
├── hangman.py   # the game
├── words.txt    # English word list (google-10000-english, no swears)
└── README.md    # this file
```

### How to run

1. Install Python 3 from https://www.python.org/downloads/
2. Open a terminal in the `hangman` folder.
3. Run:

```
python hangman.py
```

If `words.txt` is missing, the game falls back to a small built-in word list.

### How to play

1. Type a single letter (A-Z) and press Enter.
2. Correct letters are revealed in the word. Wrong letters add a part to the stick figure.
3. You win by revealing the whole word. You lose after 6 wrong guesses.
4. At the end, type `y` to play again or `n` to quit.

### Tools used

- Python 3
- VS Code
- Python standard library (`random`, `os`)

### Word list source

[google-10000-english](https://github.com/first20hours/google-10000-english) (no-swears version).
