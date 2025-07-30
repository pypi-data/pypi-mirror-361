
# SailMate  
🌊 A simple chess engine built from scratch in Python  

📦 PyPI: [sailMate](https://pypi.org/project/sailMate/)

## Overview  
SailMate is a simple chess engine built completely from scratch using Python and object-oriented programming (OOP).  
It supports standard piece movement, simple FEN strings, basic evaluation, and a minimax algorithm with alpha-beta pruning.  
You can even play against the engine from the command line.

That said, it **does not** support underpromotion, draws by repetition, or the 50-move rule. Also, since it's written in Python and not highly optimized, it runs quite slowly.  I built it mainly as a learning exercise, for fun, and to submit to Shipwrecked.

<div align="center">
  <a href="https://shipwrecked.hackclub.com/?t=ghrm" target="_blank">
    <img src="https://hc-cdn.hel1.your-objectstorage.com/s/v3/739361f1d440b17fc9e2f74e49fc185d86cbec14_badge.png" 
         alt="This project is part of Shipwrecked, the world's first hackathon on an island!" 
         style="width: 35%;">
  </a>
</div>

---

## How to Use

### Fast Install

First, install SailMate:

```bash
pip install sailMate
````

Then write the following code and run:

```python
import sailMate

sailMate.play()
```

And **BOOM**, you'll be able to play against the SailMate engine

---

### 🧠 OOP Design

**Core Components:**

* **`Piece`** *(abstract base class)*

  * `Pawn`
  * `Knight`
  * `Bishop`
  * `Rook`
  * `Queen`
  * `King`
    *(All inherit from `Piece`)*

* **`Board`** — Handles game state and possible move generation

* **`FEN`** — Parses a simple FEN string into board state

  ⚠️ This does **not** support full FEN strings.
  Please remove the trailing data after the piece layout.
  Example:

  ```
  rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
  ```

  becomes:

  ```
  rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR
  ```

  ```python
  import sailMate

  myBoard = sailMate.FEN("r1bqkbnr/pppp1ppp/2n5/4p3/3PP3/5N2/PPP2PPP/RNBQKB1R", False)
  # First parameter: simplified FEN string
  # Second parameter: who plays (True → White, False → Black)
  ```

* **`evaluate()`** — Simple material-based evaluation

  ```python
  print(sailMate.evaluate(myBoard, 0)) 
  # First parameter: board object
  # Second parameter: depth
  ```

* **`minimax()`**, **`minimaxImproved()`** — Minimax with alpha-beta pruning

  ```python
  print(sailMate.minimaxImproved(myBoard, 2)) 
  # First parameter: board object
  # Second parameter: depth
  ```

* **`play()`** — Command-line gameplay loop

---

📁 Check out `sailMate/sailMate.py` for more functions

