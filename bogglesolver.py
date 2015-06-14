#!/usr/bin/env python
import multiprocessing as mp
import dawg
import bogglegen

"""
Solves a boggleboard using words in /usr/share/dict/words.
A directed acyclic word graph is generated to represent
all words in /usr/share/dict/words.  This allows
word prefixes to be tested as we iterate through the
boggleboard.  We can therefore stop if the letters so far
are not the prefix for any word.

I used the dawg library as it is implemented in C as dawgdic
so I assumed it would be quicker than a native Python
solution. I also considered using a trie, but felt that a
dawg would be more memory-efficient as there is no repetition.

I used an iterative approach rather than a recursive one
as CPython's recursion depth limit is 1000 (although I don't
expect to reach that with this dataset) and I also assume that
an iterative approach will be better optimised by CPython.

The supplied bogglegen returned a 4x4 boggleboard,
so I increased this to 6x6 as per the problem description
by increasing the length of original_boggle_dice to 36.

Author: Adam McCarthy
"""


def get_neighbours(i, j):
    """
    returns the coordinates of all cells in proximity
    to the supplied (i,j). Does not wrap around the
    matrix.
    A B C
    D * F
    G H I
    """
    if i > 0: yield (i-1, j)  # D
    if i < len(boggleboard)-1: yield (i+1, j)  # F
    if j > 0: yield (i, j-1)  # B
    if j < len(boggleboard)-1: yield (i, j+1)  # H

    if i > 0 and j > 0: yield (i-1, j-1)  # A
    if i < len(boggleboard)-1 and j < len(boggleboard)-1:  # I
        yield (i+1, j+1)
    if i < len(boggleboard)-1 and j > 0:  # C
        yield (i+1, j-1)
    if i > 0 and j < len(boggleboard)-1:  # G
        yield (i-1, j+1)  # G


def follow_word(q, route):
    """
    tests route to determine whether it is a prefix
    or a word.  If it is a word, print it. If it is
    a prefix, add all neighbours to the queue to be
    processed next.
    """
    # build word by traversing the route
    word = u"".join(boggleboard[i][j] for i, j in route)
    # word is not a prefix or a word
    if not completion_dawg.has_keys_with_prefix(word):
        return

    # word is a word
    if word in completion_dawg:
        print("%s:\t%s" % (word, route))

    neighbours = get_neighbours(*route[-1])
    # iterate through all route[-1]'s neighbours
    # if the cell has not been visited previously, add
    # it to the queue for further processing.
    for neighbour in neighbours:
        if neighbour not in route:
            q.put(route + [neighbour])


def generate_dawg():
    # wc -l /usr/share/dict/words$ #==> 479829
    # assume UTF-8, f.readlines() ~= 479829*9bits = 4318461bits ~= 4MB
    # words is a generator to attempt to reduce memory consumption
    # during the dawg creation.
    # dawg docs claim for CompletionDAWG 3,000,000 UTF-8 words == 3MB
    # If the dataset was much larger and didn't fit in memory I 
    # could read in in chunks and do multiple passes over the boggleboard
    # I haven't had time to verify these numbers by profiling but they're
    # _very_ rough guesses.
    with open("/usr/share/dict/words", "r") as f:
        words = (word.rstrip("\n").upper() for word in f.readlines())

    return dawg.CompletionDAWG(words)


def solve_boggleboard(boggleboard, completion_dawg):
    # The fork() overhead here means that for /usr/share/dict/words
    # running multiple processes is probably slower.  I haven't
    # tested this though.  I included it in case you plan to run
    # this over larger datasets.
    q = mp.JoinableQueue()
    procs = []
    # To init, start off with every boggleboard cell in the queue
    for i in range(len(boggleboard)):
        for j in range(len(boggleboard[i])):
            q.put([(i, j)])

    # code to be run in the child processes
    # None is a sentinel to terminate the process
    def f(q):
        for item in iter(q.get, None):
            follow_word(q, item)
            q.task_done()

        q.task_done()

    for i in range(mp.cpu_count()):
        procs.append(mp.Process(target=f, args=(q,)))
        procs[-1].daemon = True
        procs[-1].start()

    # q is empty so processing has finished
    q.join()

    # instruct the processes to terminate
    for p in procs:
        q.put(None)

    q.join()

    for p in procs:
        p.join()


if __name__ == "__main__":
    completion_dawg = generate_dawg()
    boggleboard = bogglegen.gen_board(bogglegen.original_boggle_dice)

    bogglegen.print_matrix(boggleboard)
    solve_boggleboard(boggleboard, completion_dawg)
    bogglegen.print_matrix(boggleboard)

