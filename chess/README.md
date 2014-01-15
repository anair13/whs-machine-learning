whs-chess
====================

Chess interface and intelligence implemented during our senior year at 
Winchester High School.

Operating Instructions
----------------------
To play, run `python UI.py`

Files explained:
* chess.py contains the definition of the game
* UI.py contains the UI controller, written in Tkinter
* AI.py contains a working artificial intelligence
* BadAI.py plays a random valid move at every turn
* MoveTree.py is a work-in-progress to implement an AI that thinks in parallel

To build your own AI, implement a Brain which implements the `get_move` method 
and import that module from UI.py, instead of AI.py

Authors
-------
Kevin Gao  
Ashvin Nair  
