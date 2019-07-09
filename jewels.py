# implement the matching game Jewels in a machine-playable way, test
# various strategies

import random
from matplotlib import pyplot as plt
import scipy.stats as stat
from collections import Counter, defaultdict
import pickle
import os
from datetime import datetime

# global game parameters. The rockbox jewels game has width=height=8,
# numberOfColours=7, vanishLength=3
width = 8
height = 8
numberOfColours = 7  # block colours will be represented by the numbers
# 1,2,...,numberOfColours, with 0 being an empty square
vanishLength = 3  # a collection of at least vanishLength blocks of the same
# colour in a vertical or horizontal line is called a mono.


class board:
    score = 0
    entries = [[0 for i in range(width)] for j in range(height)]
    numberOfTurns = 0

    # the nump branch in github shows what happens if you store the entries
    # in a numpy array of ints - it's slower by a factor of nearly 2

    def printEntries(self):  # only for <10 colours
        for j in range(height):
            print " ".join(map(str, self.entries[j]))

    def randomize(self):
        for i in range(width):
            for j in range(height):
                self.entries[j][i] = random.randint(1, numberOfColours)

    def findMonos(self):
        # return a list whose elements correspond to the maximal monos
        # in the current board.
        # Each list element is a list of coordinates
        # making up the corresponding mono
        # if we stored the board as a numpy matrix we could extract the
        # rows or columns as vectors and so avoid writing all this stuff
        # twice...(but it turns out to be a lot slower in numpy)
        output = []
        # first, the horizontal monos
        for i in range(height):
            row = self.entries[i]
            currentColour = row[0]
            currentStreakStart = 0
            for j in range(1, width):
                if row[j] != currentColour:
                    if j - currentStreakStart >= vanishLength:
                        output.append([[i, x] for x in
                                       range(currentStreakStart, j)])
                    currentColour = row[j]
                    currentStreakStart = j
            # we hit the last entry, j=width. Was it the last entry of a
            # mono? if so, append it.
            if width - currentStreakStart >= vanishLength:
                output.append([[i, x] for x in
                               range(currentStreakStart, width)])
        # now the vertical monos
        for j in range(width):
            currentColour = self.entries[0][j]
            currentStreakStart = 0
            for i in range(1, height):
                if self.entries[i][j] != currentColour:
                    if i - currentStreakStart >= vanishLength:
                        output.append([[x, j] for x in
                                       range(currentStreakStart, i)])
                    currentColour = self.entries[i][j]
                    currentStreakStart = i
            # we hit the last entry of the column, was it the last entry
            # of a mono? if so, append it to output
            if height - currentStreakStart >= vanishLength:
                output.append([[x, j] for x in
                               range(currentStreakStart, height)])

        return output

    def gravity(self):
        for j in range(width):
            col = [self.entries[i][j] for i in
                   range(height) if self.entries[i][j] != 0]
            newcol = [0 for x in range(height - len(col))] + col
            # make the first col equal to newcol
            for i in range(height):
                self.entries[i][j] = newcol[i]

    def randomFillZeroes(self):
        for i in range(height):
            for j in range(width):
                if self.entries[i][j] == 0:
                    self.entries[i][j] = random.randint(1, numberOfColours)

    def evolve(self):
        # repeat:
        #   zero out any monos
        #   update the score
        #   gravity
        #   random fill any spaces
        # until there are no more monos.
        # return the number of chain reactions caused
        chains = -1
        while len(self.findMonos()) != 0:
            chains += 1
            monos = self.findMonos()
            for m in monos:
                self.score += len(m) - vanishLength + 1
                for x in m:
                    self.entries[x[0]][x[1]] = 0
            self.gravity()
            self.randomFillZeroes()
        return chains

    def horizontalMonoContaining(self, coords):
        # does self.entries contain a horizontal mono containing the entry
        # coords?
        colour = self.entries[coords[0]][coords[1]]
        ll = 0
        while True:
            if ((coords[1] + ll >= width) or
                    (self.entries[coords[0]][coords[1] + ll] != colour)):
                break
            else:
                ll += 1
        r = 0
        while True:
            if ((coords[1] - r < 0) or
                    (self.entries[coords[0]][coords[1] - r] != colour)):
                break
            else:
                r += 1
        return ll + r - 1 >= vanishLength

    def verticalMonoContaining(self, coords):
        # does self.entries contain a vertical mono containing the entry
        # coords?
        colour = self.entries[coords[0]][coords[1]]
        d = 0
        while True:
            if ((coords[0] + d >= height) or
                    (self.entries[coords[0] + d][coords[1]] != colour)):
                break
            else:
                d += 1
        u = 0
        while True:
            if ((coords[0] - u < 0) or
                    (self.entries[coords[0] - u][coords[1]] != colour)):
                break
            else:
                u += 1
        return u + d - 1 >= vanishLength

    def legitMoves(self):
        # Moves swap two entries which are adjacent horizontally or vertically.
        # A move is legit iff it creates a new mono.
        # This function returns a list of all legit moves, as a list of pairs
        # of coordinates, and the number of legitimate moves.
        numberLegitMoves = 0
        listOfMoves = []
        for i in range(height):
            for j in range(width):
                if (j < width - 1) and (self.entries[i][j] !=
                   self.entries[i][j + 1]):
                    # it makes sense to swap [i,j] and [i,j+1]. does that
                    #  create a new mono?
                    # copy.deepcopy is really slow, so we'll apply the move,
                    #  test for monos, then apply it again to get back where we
                    # started
                    self.applyMove([[i, j], [i, j + 1]])
                    # now look for monos. There can be four kinds:
                    #  1. vert mono containing [i,j+1] of colour entries[i][j]
                    #  2. vert mono containing [i,j] of colour entries[i][j+1]
                    #  3. horiz mono finishing [i,j] of colour entries[i][j+1]
                    #  4. horiz mono starting [i,j+1] of colour entries[i][j]
                    if (self.verticalMonoContaining([i, j + 1]) or
                            self.verticalMonoContaining([i, j]) or
                            self.horizontalMonoContaining([i, j]) or
                            self.horizontalMonoContaining([i, j + 1])):
                        numberLegitMoves += 1
                        listOfMoves.append([[i, j], [i, j + 1]])
                    self.applyMove([[i, j], [i, j + 1]])  # get self.entries
                    # back to where it was before
                if ((i < height - 1) and
                        (self.entries[i][j] != self.entries[i + 1][j])):
                    # it makes sense to swap [i,j] and [i+1,j]. does that
                    # create a new mono?
                    self.applyMove([[i, j], [i + 1, j]])
                    if (self.verticalMonoContaining([i, j]) or
                            self.verticalMonoContaining([i + 1, j]) or
                            self.horizontalMonoContaining([i, j]) or
                            self.horizontalMonoContaining([i + 1, j])):
                        numberLegitMoves += 1
                        listOfMoves.append([[i, j], [i + 1, j]])
                    self.applyMove([[i, j], [i + 1, j]])
        return listOfMoves, numberLegitMoves

    def applyMove(self, move):
        firstrow = move[0][0]
        firstcol = move[0][1]
        secondrow = move[1][0]
        secondcol = move[1][1]
        temp = self.entries[firstrow][firstcol]
        self.entries[firstrow][firstcol] = self.entries[secondrow][secondcol]
        self.entries[secondrow][secondcol] = temp


# strategies:
        # choose randomly from all available moves
        # choose randomly from highest few moves available
        # choose reandomly from lowest few moves
        # mixed
        # approximate the play that maximises something or other

def testStrategy(chooser, numberOfGames):
    # a strategy is a way of choosing moves. testStrategy takes
    # a function `chooser' which accepts a list of moves and returns
    # one of them, and a number numberOfGames, and runs numberOfGames
    # games using chooser to pick from the available moves.
    # It returns the list of scores from those games and the list of game
    # lengths.
    #
    # Log the deltas for each possible number of
    # available moves ("position"), and compare the distributions.
    # deltasByPosition should be a defaultdict:
    # deltasByPosition = defaultdict(list), then dbp[n].append(delta)
    # keys = number n of moves available,
    # deltasByPosition[n] = list of deltas for that number n of moves available
    #
    # meanHeights is a dict whose [n] value is a list. The list has one element
    # for each time there were n moves available.  This element is the mean
    # height of all the moves available at that time.
    scores = []
    lengths = []
    deltaMovesAvailable = []
    initialMovesAvailable = []
    maxMovesAvailable = []
    chains = []
    allMovesAvailable = []
    deltasByPosition = defaultdict(list)
    meanHeightMovesAvailableByPosition = defaultdict(list)
    for i in range(numberOfGames):
        b = board()
        b.randomize()
        movesAvailableThisGame = []
        while True:
            chains.append(b.evolve())
            moves, numberOfAvailableMoves = b.legitMoves()
            movesAvailableThisGame.append(numberOfAvailableMoves)
            if numberOfAvailableMoves == 0:
                scores.append(b.score)
                lengths.append(b.numberOfTurns)
                deltas = [movesAvailableThisGame[i + 1] -
                          movesAvailableThisGame[i]
                          for i in range(len(movesAvailableThisGame) - 1)]
                deltaMovesAvailable += deltas
                for i in range(len(movesAvailableThisGame) - 1):
                    deltasByPosition[movesAvailableThisGame[i]].append(deltas[i])
                initialMovesAvailable.append(movesAvailableThisGame[0])
                maxMovesAvailable.append(max(movesAvailableThisGame))
                allMovesAvailable += movesAvailableThisGame
                break
            # the break lets us assume numberOfAvailableMoves != 0
            meanHeight = sum([x[0][0] for x in moves]) / (1.0 * numberOfAvailableMoves)
            meanHeightMovesAvailableByPosition[numberOfAvailableMoves].append(meanHeight)
            b.applyMove(chooser(moves))
            b.numberOfTurns += 1

    statsAndPlots(scores, lengths, deltaMovesAvailable, initialMovesAvailable,
                  maxMovesAvailable, deltasByPosition, chains, allMovesAvailable, meanHeightMovesAvailableByPosition)


def statsAndPlots(scores, lengths, deltaMovesAvailable, initialMovesAvailable,
                  maxMovesAvailable, deltasByPosition, chains, allMovesAvailable, meanHeightMovesAvailableByPosition):
    # Produce plots and statistics, write them to disk in a sensible manner
    #
    # Note: scipy.stats.kurtosis produces the *excess* kurtosis by default

    ##################################
    # create a directory for writing #
    ##################################

    # create a subdirectory of where the script is running named with the
    # current date and time
    todayString = datetime.today().replace(microsecond=0).isoformat()
    # e.g. '2019-05-01T16:20:47', ok as a unix directory name
    os.mkdir(todayString)
    cwd = os.path.dirname(os.path.abspath(__file__))
    pat = os.path.join(cwd, todayString)
    # now pat is the path to the directory in which we'll do our logging
    f = open(pat + "/stats.txt", "w+")
    # we'll log all stats to this file

    ######################
    # scores and lengths #
    ######################

    plt.hist(scores, density=True, bins=70)
    plt.title("scores density")
    plt.savefig(pat + "/scoresDensity.svg", format='svg')
    plt.show()

    op = "scores " + str(stat.describe(scores)) + "sd " + str(stat.tstd(scores))
    print op
    f.write(op + "\n")

    plt.hist(lengths, density=True, bins=70)
    plt.title("lengths density")
    plt.savefig(pat + "/lengthsDensity.svg", format='svg')
    plt.show()

    op = "lengths " + str(stat.describe(lengths)) + "sd " + str(stat.tstd(lengths))
    print(op)
    f.write(op + "\n")

    plt.scatter(lengths, scores)
    plt.title("lengths vs scores")
    plt.savefig(pat + "/lengthsVscores.svg", format='svg')
    plt.show()

    op = "sample corr coeff lengths-scores " + str(stat.pearsonr(lengths, scores))
    print op
    f.write(op + "\n")

    ###############
    # move deltas #
    ###############

    expectedJumps = []
    positions = []
    variances = []
    kurtoses = []
    sds = []
    skewnesses = []

    for k in deltasByPosition.keys():
        positions.append(k)
        expectedJumps.append(stat.tmean(deltasByPosition[k]))
        descr = stat.describe(deltasByPosition[k])
        variances.append(descr.variance)
        kurtoses.append(descr.kurtosis)
        sds.append(descr.variance ** 0.5)
        skewnesses.append(descr.skewness)
        op = "available moves " + str(k) + " delta dist " + str(descr)
        print op
        f.write(op + "\n")

    for k in [1, 4, 8, 12, 16]:  # dbp.keys():
        n = len(deltasByPosition[k])
        c = Counter(deltasByPosition[k])
        xvalues = sorted(c.keys())  # weird results for plotting lines unless
        # x-values sorted
        yvalues = [c[key] / (n * 1.0) for key in xvalues]
        plt.plot(xvalues, yvalues, label=str(k))

    plt.legend()
    plt.title("available move deltas by position")
    plt.savefig(pat + "/move_deltas_by_position.svg", format='svg')
    plt.show()

    for k in [1, 4, 8, 12, 16]:
        c = Counter(deltasByPosition[k])
        xvalues = sorted(c.keys())
        xtrunc = [x for x in xvalues if x >= -1]
        n = sum([c[key] for key in xtrunc])
        yvalues = [c[key] / (n * 1.0) for key in xtrunc]
        plt.plot(xtrunc, yvalues, label=str(k))

    plt.legend()
    plt.title("move deltas by position, ignoring steps <-1")
    plt.savefig(pat + "/conditional_move_deltas_by_position.svg", format='svg')
    plt.show()

    plt.plot(positions, expectedJumps)
    plt.title("position - expected jump")
    plt.savefig(pat + "/position_vs_expected_jump.svg", format='svg')
    plt.show()

    plt.plot(positions, variances)
    plt.title("position - variance of jumps")
    plt.savefig(pat + "/position_variance.svg", format='svg')
    plt.show()

    plt.plot(positions, sds)
    plt.title("position - sd of jumps")
    plt.savefig(pat + "/position_sd.svg", format='svg')
    plt.show()

    plt.plot(positions, kurtoses)
    plt.title("position - kurtosis")
    plt.savefig(pat + "/position_kurtosis.svg", format='svg')
    plt.show()

    plt.plot(positions, skewnesses)
    plt.title("position - skewness")
    plt.savefig(pat + "/skewness.svg", format='svg')
    plt.show()

    plt.hist(deltaMovesAvailable, density=True, bins=range(min(deltaMovesAvailable) - 2, max(deltaMovesAvailable) + 2))
    plt.title("available move deltas overall")
    plt.savefig(pat + "/available_move_deltas.svg", format='svg')
    plt.show()

    op = "deltas " + str(stat.describe(deltaMovesAvailable)) + " sd " + \
        str(stat.tstd(deltaMovesAvailable))
    print op
    f.write(op + '\n')

    #################################################################
    # initial, max, all numbers of moves available, chain reactions #
    #################################################################

    plt.hist(initialMovesAvailable, density=True, bins=range(max(initialMovesAvailable) + 2))
    plt.title("initial number of moves available")
    plt.savefig(pat + "/initialMovesAvailable.svg", format='svg')
    plt.show()

    op = "initial moves" + str(stat.describe(initialMovesAvailable))
    print op
    f.write(op + '\n')

    plt.hist(maxMovesAvailable, bins=range(max(maxMovesAvailable) + 2))
    plt.title("max number moves available")
    plt.savefig(pat + "/maxMovesAvailable.svg", format='svg')
    plt.show()

    op = "max moves " + str(stat.describe(maxMovesAvailable))
    print op
    f.write(op + '\n')

    plt.hist(chains, bins=range(max(chains) + 2), density=True, align="left")
    plt.title("number of chain reactions caused")
    plt.savefig(pat + "/chains.svg", format='svg')
    plt.show()

    averageChainReactions = sum(chains) * 1.0 / len(chains)
    numberChainReactions = len([x for x in chains if x > 0])
    proportionChainReactions = numberChainReactions * 1.0 / len(chains)
    op = "avg no. chain reactions per move " + str(averageChainReactions) + \
         " proportion of moves causing a cr " + str(proportionChainReactions)
    print op
    f.write(op + '\n')

    plt.hist(allMovesAvailable, bins=range(max(allMovesAvailable) + 2), density=True)
    plt.title("number of moves available")
    plt.savefig(pat + "/allMovesAvailable.svg", format='svg')
    plt.show()
    op = "moves avail " + str(stat.describe(allMovesAvailable))
    print op
    f.write(op + '\n')

    ################
    # move heights #
    ################

    means = []
    for k in meanHeightMovesAvailableByPosition.keys():
        mn = stat.tmean(meanHeightMovesAvailableByPosition[k])
        means.append(mn)

    plt.scatter(meanHeightMovesAvailableByPosition.keys(), means)
    plt.title("x = number of moves avail, y = mean height of moves avail")
    plt.savefig(pat + "/heightMovesAvailByPosn.svg", format='svg')
    plt.show()

    f.close()

    ############
    # Pickling #
    ############

    def pick(name, obj):
        with open(pat + "/" + name + ".pkl", 'wb') as output:
            pickle.dump(obj, output)
    # save the available moves distribution for simulation
    counts = Counter()
    for d in deltaMovesAvailable:
        counts[d] += 1
    pick("deltacounter", counts)
    pick("scores", scores)
    pick("lengths", lengths)
    pick("deltaMovesAvailable", deltaMovesAvailable)
    pick("initials", initialMovesAvailable)
    pick("maxes", maxMovesAvailable)
    pick("deltas by posn", deltasByPosition)
    pick("allMovesAvailable", allMovesAvailable)
    pick("height by position", meanHeightMovesAvailableByPosition)


##########################
# some chooser functions #
##########################


def randomChooser(moves):
    return random.choice(moves)


def chooseFromTop3(moves):
    # pick randomly from the 3 moves nearest the top
    movesSortedByRow = sorted(moves, key=lambda x: x[0][0])
    return random.choice(movesSortedByRow[:3])


def chooseFromTop2(moves):
    # pick randomly from the 2 moves nearest the top
    movesSortedByRow = sorted(moves, key=lambda x: x[0][0])
    return random.choice(movesSortedByRow[:2])


def chooseTop1(moves):
    movesSortedByRow = sorted(moves, key=lambda x: x[0][0])
    return movesSortedByRow[0]


def chooseFromHighest(moves):
    # pick randomly from the highest moves
    movesSortedByRow = sorted(moves, key=lambda x: x[0][0])
    highestRowWithMoves = movesSortedByRow[0][0][0]
    highestMoves = [movesSortedByRow[0]]
    for i in range(1, len(movesSortedByRow)):
        if movesSortedByRow[i][0][0] == highestRowWithMoves:
            highestMoves.append(movesSortedByRow[i])
        else:
            break
    return random.choice(highestMoves)


def chooseLastHighest(moves):
    movesSortedByRow = sorted(moves, key=lambda x: x[0][0])
    highestRowWithMoves = movesSortedByRow[0][0][0]
    highestMoves = [movesSortedByRow[0]]
    for i in range(1, len(movesSortedByRow)):
        if movesSortedByRow[i][0][0] == highestRowWithMoves:
            highestMoves.append(movesSortedByRow[i])
        else:
            break
    return highestMoves[-1]


def chooseBottom3(moves):
    # pick randomly from the 3 moves nearest the bottom
    movesSortedByRow = sorted(moves, key=lambda x: x[0][0])
    return random.choice(movesSortedByRow[-1:])


##################################
# run the test, plot the results #
##################################

testStrategy(chooseBottom3, 5000)


# # export scores data in R-readable format
# f = open("/home/mjt/Dropbox/code/python/jewels/chooseFromHighest_scores.txt",
#          "a")
# r_string = "\nx=c(" + ",".join(map(str, scores)) + ")"
# # use source("scores.txt") in R to load this
# f.write(r_string)
# f.close()
