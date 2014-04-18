#!/usr/bin/python
# blame: Ray C. He rayhe@mit.edu

import sys
import random
import re
import string

class MarkovLibrary:
    # a markov library, a repository of three word chains
    # dictionary of dictionaries of arrays for great justice
    chains = None
    #stuff that shouldn't get spaces
    nospace = re.compile('\w')
    def __init__(self):
        self.chains = {}

    # inserts a chain of first, second, third into a
    # lookup table. appends the third to the array of possible
    # thirds
    def insert_chain(self, first, second, third):
        if (first not in self.chains):
            self.chains[first] = {}
        if (second not in self.chains[first]):
            self.chains[first][second] = []
        self.chains[first][second].append(third)

    # returns a random phrase, calls recursively
    def get_random(self):
        first = '(START)'
        # randomly pick among the starters
        second = random.sample(self.chains[first].keys(),1)[0]
        return second + self.__get_random(first,second);

    # private __get_random which allows the library to specify
    # a first and second to lookup
    def __get_random(self, first, second):
        third = self.__get_third(first,second)
        if (third == '.'):
            return '.'
        separator = ' '
        if (not self.nospace.match(third)):
            separator = ''

        return separator + third +  self.__get_random(second,third)

    def __get_third(self, first, second):
        if (first not in self.chains):
            raise Exception("first not found")
        if (second not in self.chains[first]):
            raise Exception("second not found")
        if (len(self.chains[first][second]) == 0):
            raise Exception("no existing target words")
        return random.sample(self.chains[first][second],1)[0]

def main():
    filename = "/usr/local/CoffeeScale/taoteching.txt"
    #argv should contain the file name
    #if (len(argv) != 1):
    #    print "usage: python mkgen.py <filename>"
    #    sys.exit()
        
    # grab the filename, which should be the only argument
    #filename = argv[0]
    ml = MarkovLibrary()

    # our regexs
    unused = re.compile('"')
    punctuation = re.compile('\W')
    spacing = re.compile('\s+')

    
    fd = open(filename);
    # line starts as nothing
    line = ''
    for li in fd:
        #get rid of annoying trailing/leading whiespace
        li=string.rstrip(string.lstrip(li))
        if (len(li) == 0 or li[0].isdigit()):
            continue
        line += li + ' '
        if (li[-1] != '.'):
            # keep reading until we get a period
            continue

        oldline = line
        line = unused.sub('',line)
        # put spaces around punctuation so they play nice with split
        line = punctuation.sub(lambda m: ' '+m.group()+' ', line)
        # split the line into words
        words = spacing.split(line)
        # filter out unreplaced words (mostly whitespaces at end of
        # sentences that passed the split as zero-length strings)
        words = filter(lambda w: w!='', words)
        if (len(words) == 0):
            continue
        words.insert(0,'(START)')
        line = '' # reset line
        # used for debug
        #print oldline
        #print words
        for i in range(0, len(words)-2):
            ml.insert_chain(words[i],words[i+1],words[i+2])

    #print ml.get_random()
    return ml.get_random()

if __name__ == "__main__":
    main(sys.argv[1:])
