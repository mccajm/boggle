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
