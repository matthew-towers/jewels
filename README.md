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
higher moves when they are plentiful.  Preliminary results are that
always playing near the top is a lot better than playing at
random.

`jewels.py` is mostly a Python class called `board` with methods for
applying moves, evolving the board and keeping track of score, finding
available moves and so on, all in a simplified version of the game.
There are a few strategies implemented as move-chooser functions and a
loop for playing a number of games using a fixed strategy, logging the
scores obtained, displaying it using `pyplot`, and writing it to an `R`-readable file.

## Some results

Choosing completely at random from available monos gives a mean score of
about 103 (standard deviation about 87, median 77).  The following plot
shows the empirical density function obtained by running 100000 games
(more than enough to get a good estimate of the mean if the standard
deviation is
really around 87);
the blue dashed vertical line shows the mean score.
![Empirical density plot for scores obtained by randomly choosing monos](https://raw.githubusercontent.com/silverfish707/jewels/master/randomchoices.svg?sanitize=true)

Choosing randomly amongst the highest monos on the board does a lot
better (mean score 298, median 219, standard deviation 268). Here's a
density plot based on 50000 games (fewer than before because it takes a
lot longer).
![Empirical density plot for scores obtained by choosing amongst the highest monos](https://raw.githubusercontent.com/silverfish707/jewels/master/chooseFromHighest.svg?sanitize=true)
