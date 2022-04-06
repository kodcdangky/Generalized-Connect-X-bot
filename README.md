# Generalized Connect Four bot
A bot to play any variations of Connect Four, whether that's on a 10x10 board instead of the original 7x6 board, or playing for 5, 6,... in a line instead of 4
## Video demo: https://youtu.be/w0epFK8nG_g

## Usage/Installation
Requires Python 3.10.

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
- basics.py: Where all the magic happens. Change the constants ROWS, COLS, CONNECT, at the top of the file to change the configuration of the Connect version you wish to play. Non-8x8 boards look a bit janky, however.

## Approach

### Heuristic:
The heuristic of each state is calculated by counting the number of open-3s (or rather, number of connect - 1) of each side while also accounting for how many moves does it take to make a full line with that open line, then calculate the difference between the 2 players. If the heuristic is positive, then the maximizing player has the advantage, and vice versa.

### Depth-limited minimax with alpha-beta pruning:
This bot uses depth-limited minimax with alpha-beta pruning to determine its next move.

Per branch, all smaller branches which are not pruned are added to a list, which then gets sorted and trimmed to keep only the best moves, then a move is selected randomly from the trimmed list. This ensures that when given a state that is commonly seen with multiple options that has the same score, e.g. the opening state, the bot doesn't make the same option every time.

#### Limitation:
The downside to my approach is that branches cannot be pruned as early as the traditional alpha-beta pruning, since we want to keep all equally best options. As such, a branch can only be pruned if it is confirmed that it will be worse than the previously considered-worst branch, and not worse or equal to, leading to higher time complexity as more branches are considered.

To offset this, the list of possible moves is (naively) sorted before looping through, in the hopes that the best possible moves are considered first, so that the later moves are pruned as early as possible. Considering that moves that are closer to the center of the board have a higher chance of making a connection, these moves are considered first, followed by moves on the edges, followed by moves in the corners.

All of this is to say: I sorted the list of possible moves in order of the Manhattan distance of each move to the center of the board. There's no consideration to the current state of the game, hence 'naive'.

## Final thoughts
With some changes, this bot can be used to play any generalized version of Tic Tac Toe as well, although it would have to either return to the normal pruning approach, or sort the list of possible moves more intelligently, as on any same board size, Tic Tac Toe has many more possible moves than Connect Four. (As I'm writing this, my first thought about sorting the list of possible moves is to sort moves by how far away they are from any cluster of non-empty cells, maybe that's enough? Probably not though)

As for how well the bot can play, I am fairly satisfied with the heuristic I am using currently. While it certainly could be better, this heuristic was easy to implement, and I could only sometimes beat it. (Although to be fair I have not played a single Connect Four game before I made this bot, so most likely I'm just a bad player ¯\\\_(ツ)_/¯ )

## References
[CS50 2020 - Artificial Intelligence](https://youtu.be/eey91kzfOZs) CS50 Lecture on AI by Brian Yu. If you want a complete beginner lecture on AI for people who are familiar with programming but absolutely not a single thing about AI, this is where to start, because before this I know as much about AI as I do about working for NASA. (Not to say that I'm any closer to working for NASA now than I was before but I did manage to write this bot)

[Algorithms Explained – minimax and alpha-beta pruning](https://youtu.be/l-hh51ncgDI) A visualization of both vanilla minimax and minimax with alpha-beta pruning with explanation and code example by Sebastian Lague. An absolute godsent of a video and I cannot stress how highly I recommend it.

[Connect 4 AI: How it Works](https://roadtolarissa.com/connect-4-ai-how-it-works/) Part 1 of a blog post by Adam Pearce. This is where I got my idea for the heuristic function, in which I added my weight system to this idea.
