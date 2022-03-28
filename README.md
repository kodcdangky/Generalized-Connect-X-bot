# Generalized Connect Four bot
## Video demo: https://youtu.be/w0epFK8nG_g
## Description
A bot to play any variations of Connect Four, whether that's on a 10x10 board instead of the original 7x6 board, or playing for 5, 6,... in a line instead of 4

## Usage/Installation
Requires Python.

Developed with Python 3.10, as such I do not know if this is compatible with older versions of Python, so Python 3.10 is recommended.

Download the source files, open terminal from the folder you saved the files in, and run
```
python console.py
```
to play the console version of the game, or
```
python graphics.py
```
to play the pygame version of the game. Requires [pygame](https://www.pygame.org/wiki/GettingStarted#Pygame%20Installation)

## Source files
- console.py: The console version of the game
- graphics.py: The pygame version of the game. Requires [pygame](https://www.pygame.org/wiki/GettingStarted#Pygame%20Installation)
- basics.py: Where all the magic happens. Change the constants ROWS, COLS, CONNECT, at the top of the file to change the configuration of the Connect version you wish to play.

## Approach

### Heuristic:
The heuristic of each state is calculated by counting the number of open-3s (or rather, number of connect - 1) of each side while also accounting for how many moves does it take to make a full line with that open line, then calculate the difference between the 2 players. If the heuristic is positive, then the maximizing player has the advantage, and vice versa.

### Depth-limited minimax with alpha-beta pruning:
This bot uses depth-limited minimax with alpha-beta pruning to determine its next move.

Per choice branch, all smaller branches which are not pruned are added to a list, which then gets sorted and trimmed to keep only the best moves, then a move is selected randomly from the trimmed list. This ensures that when given a state that is commonly seen with multiple options that has the same score, e.g. the opening state, the bot doesn't make the same option every time.

#### Limitation:
The downside to this approach is that branches cannot be pruned as early as the traditional approach, since we want to keep all equally best options. As such, a branch can only be pruned if it is confirmed that it will be worse than the previously considered-worst branch, and not worse or equal to, leading to higher time complexity as more branches are considered.

To offset this, the list of possible moves is (naively) sorted before looping through, in the hope that the best possible moves are considered first, so that the later moves are pruned as early as possible. Considering that moves that are closer to the center of the board have a higher chance of making a connection, these moves are considered first, followed by moves on the edges, followed by moves in the corners.

All of this is to say: I sorted the list of possible moves in order of the manhanttan distance of each move to the center of the board. There's no consideration to the current state of the game, hence 'naive'.

## References
[CS50 2020 - Artificial Intelligence](https://youtu.be/eey91kzfOZs) CS50 Lecture on AI by Brian Yu. If you want a complete beginner lecture on AI for people who are familiar with programming but absolutely not a single thing about AI, this is where to start, because before this I know as much about AI as I do about working for NASA. (Not to say that I'm any closer to working for NASA now than I was before but I did manage to write this bot)

[Algorithms Explained – minimax and alpha-beta pruning](https://youtu.be/l-hh51ncgDI) A visualization of both vanilla minimax and minimax with alpha-beta pruning with explanation and code example by Sebastian Lague. An absolute godsent of a video and I cannot stress how highly I recommend it.

[Connect 4 AI: How it Works](https://roadtolarissa.com/connect-4-ai-how-it-works/) Part 1 of a blog post by Adam Pearce. This is where I got my idea for the heuristic function, in which I added my weight system to this idea.