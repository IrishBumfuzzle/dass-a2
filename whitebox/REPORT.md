# Whitebox testing

## 1.1 Control flow graph


## 1.2 Code Quality analysis

**Iteration 1**
- Added docstrings to functions in main.py

**Iteration 2** (property.py)
- Addded module docstring
- Removed 2 attrs from Property class (both were unused)
- Removed argument from Property class
- Removed the else after return in Property.unmortage
- Added docstring to PropertyGroup

**Iteration 3** (cards.py)
- Formatted to have smaller length lines
- Added docstring

**Iteration 4** (boards.py)
- == True to just checking true
- Added docstring

**Iteration 5** (player.py)
- Remove import
- Add final newline
- Added docstring
- Remove unused var
- Removed is_elim attr

**Iteration 6** (game.py)
- Added docstring
- Made fstring to normal string
- Removed unused imports
- Removed unnecessary parens after not keyword
- Added final newline
- Removed setting player is eliminated
- Consolidated chance_deck and community_deck into a dictionary to reduce instance attributes
- Updated all references to use new decks dict structure
- Removed running attribute
- Extracted card action handling into separate private methods to reduce branching error

**Iteration 7** (config.py)
- Added module docstring for documentation

**Iteration 8** (player.py)
- Removed unused variable from move() method

**Iteration 9** (dice.py)
- Added module docstring
- Removed unused import of BOARD_SIZE
- Moved doubles_streak attribute initialization into __init__

**Iteration 10** (bank.py)
- Added module docstring
- Added Bank class docstring for clarity
- Removed unused math import

**Iteration 11** (ui.py)
- Added module docstring
- Specified exception type (ValueError)
