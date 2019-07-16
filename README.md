# jewels
Jewels is a [Rockbox](https://www.rockbox.org) plugin game similar to
Candy Crush and lots of others ([wiki says](https://en.wikipedia.org/wiki/Shariki) the original was by a Russian programmer in the 90s). You begin with a rectangular grid filled with
squares of various colours.  When there are three or more squares of the
same colour in a horizontal or vertical line (a *mono*) they disappear, your score
increases, then the blocks above them fall down to fill their place and are
replaced at the top with randomly chosen new ones.  A move swaps two horizontally or
vertically adjacent blocks to create a mono; when there are no moves
available
the game is over.

I used to play Jewels with the strategy of trying to make moves near the
top of the board, but I got to wondering whether there was a simple
better alternative: maybe a mixed strategy that involves playing lower
moves when there aren't many available in order to shake things up, and
higher moves when they are plentiful.

`jewels.py` is mostly a Python class called `board` with methods for
applying moves, evolving the board and keeping track of score, finding
available moves and so on, all in a simplified version of the game.
There are a few strategies implemented as move-chooser functions and a
loop for playing a number of games using a fixed strategy, logging data
about these games, plotting it with `matplotlib.pyplot`, and writing out some of the data for
future analysis.

## Some results

Here are score plots for random move choice and for choosing amongst the
highest few moves available.  Note the different scales on the x-axis:
playing near the top is almost three times better on average.

![Empirical density plot for scores obtained by randomly choosing monos](https://raw.githubusercontent.com/silverfish707/jewels/master/randomchoices.svg?sanitize=true)

![Empirical density plot for scores obtained by choosing amongst the highest monos](https://raw.githubusercontent.com/silverfish707/jewels/master/chooseFromHighest.svg?sanitize=true)

The following plots are based on 500000 games in which the computer
used the `chooseFromHighest` move choice function in `jewels.py`.

![number of moves available to choose from versus mean height of moves
available](https://raw.githubusercontent.com/silverfish7070/jewels/master/heightMovesAvailByPosn.svg?sanitize=true)

In the plot above, the x-axis is the number of moves left to choose from
and the height of the blob is the average height of the moves available.
Height 0 is the top row of the board, height 1 is the second row from
the top, and so on (sorry).  What you can see is how naive my comment
in the last section was: the "play near the top" strategy *automatically* implements
"play near the bottom (bigger "height") when there aren't many moves left."

![average change in number of moves available versus number of moves available](https://raw.githubusercontent.com/silverfish7070/jewels/master/move_deltas_by_position.svg?sanitize=true)

Let the number of moves available at move *t* be X<sub>t</sub>, and let
&delta; <sub>t</sub> = X<sub>t+1</sub>-X<sub>t</sub>. These plots are empirical density functions
for &delta;<sub>t</sub> | X<sub>t</sub> = x, for x=1,4,8,12,16.  In other words, they
tell us about how the number of moves available tends to change when we
make a play using the `chooseFromHighest` strategy when there is only one move to pick from, and when there are 4
moves to pick from, and when there are 8, 12, and 16 moves to pick from.

You can see that when there's just one move
left, on average we end up with more playable moves on the next turn
(mean increase is about 1.6) whereas when there is 16 moves available,
we tend to end up with fewer moves available on the next move (mean
decrease is about 1.6). The distributions have a similar character to
the [Ehrenfest model](https://en.wikipedia.org/wiki/Ehrenfest_model) or
the drunk-in-a-valley random walk.  The next plot gives a clearer view
of the expected change in number of moves available:

![mean change in number of moves available versus number of moves
available](https://raw.githubusercontent.com/silverfish7070/jewels/master/position_vs_expected_jump.svg?sanitize=true)

