import re
from typing import List
from cached_path import cached_path

import math
import functools
import sys
import pickle

import os
import tempfile
import numpy as np
from collections import defaultdict
from pylab import *
import pickle
import argparse

def connect (words, bond):
    N = len (words)
    n = 0
    sentence = []
    while (n < N):
        flag = bond[n]
        if flag == 0:
            sentence.append (words[n])
            n += 1
        else:
            sentence.append (words[n] + '_' + words[n+1])
            n += 2
    return sentence


def collocate (words, phrases):
    N = len(words)
    bond = []
    for n in range(N-1):
        (v,w) = (words[n],words[n+1])
        if (v,w) in phrases:
            bond.append (phrases[(v,w)]) # NPMI > 0
        else:
            bond.append (0)
    bond.append (0)
    # collocate max-first
    while True:
        s = max (bond)
        n = bond.index (s)
        if s == 0:
            break
        # connect maximum
        bond[n] = -1
        if n > 0:
            bond[n-1] = 0
        if n < N-2:
            bond[n+1] = 0
    # join words
    return connect (words, bond)


def parse_write (file, phrases, output):
    with open (file, 'r') as fh:
        with open (output, 'w') as oh:
            for line in fh:
                words = line.rstrip('\n').split()
                if len(words) > 0:
                    sentence = collocate (words, phrases)
                    #print("sentence:", sentence)
                    oh.write (' '.join (sentence) + '\n')
    return output


# for Myanmar language, default threshold=0.2 and default minfreq=5 is best with "corpus2" training corpus
# for Japanese language, threshold=0.1 and minfreq=1 set by researcher Daichi Mochihashi.
def compute_phrase (unigram, bigram, threshold, minfreq):
    N = sum (list(unigram.values()))
    phrases = {}
    #print(bigram.items())
    for bi,freq in bigram.items():
        if freq >= minfreq:
            v = bi[0]; w = bi[1]
            # print("N:", N, "v:", v, "w:", w, "unigram[v]:", unigram[v], "unigram[w]:", unigram[w])
            npmi = (log(N) + log(freq) - log(unigram[v]) - log(unigram[w])) \
                    / (log(N) - log(freq))
            if npmi > threshold:
                phrases[bi] = npmi
    #print("phrases: ", phrases)
    return phrases


def count_bigram (file, bigram_dict_txt, bigram_dict_bin):
    fileBI_txt = open(bigram_dict_txt, "w")
    bigram  = defaultdict (int)
    with open (file, 'r') as fh:
        for line in fh:
            words = line.rstrip('\n').split()
            if len(words) > 0:
                pword = words[0]
                for word in words[1:]:
                    bigram[(pword,word)] += 1
                    pword = word
    for key, value in bigram.items():
        fileBI_txt.write (str(key)+'\t'+str(value)+'\n')

    fileBI_txt.close()
    
    #new_bigram = {} # got error
    new_bigram = defaultdict(int)
    # removed "_" for phrase option or phrase segmentation
    for key, value in bigram.items():
        keyi1 = key[0].replace('_', '')
        keyi2 = key[1].replace('_', '')
        new_bigram[(keyi1,keyi2)]  = value
    
    # write binary dictionary
    fileBI_bin = open(bigram_dict_bin, "wb")
    pickle.dump(new_bigram, fileBI_bin)
    fileBI_bin.close()
    new_bigram.clear()
                
    return bigram


def count_unigram (file, unigram_dict_txt, unigram_dict_bin):
    fileUNI_txt = open(unigram_dict_txt, "w")
    unigram = defaultdict (int)
    with open (file, 'r') as fh:
        for line in fh:
            words = line.rstrip('\n').split()
            for word in words:
                unigram[word] += 1
    for key, value in unigram.items():
        fileUNI_txt.write (str(key)+'\t'+str(value)+'\n')
        
    fileUNI_txt.close()
    
    #new_unigram = {}, got error
    new_unigram = defaultdict(int)
    # removed "_" for phrase option or phrase segmentation       
    new_unigram = { key.replace('_', ''): value for key, value in unigram.items() }
    # write binary dictionary
    fileUNI_bin = open(unigram_dict_bin, "wb") 
    pickle.dump(new_unigram, fileUNI_bin)

    fileUNI_bin.close()      
    #new_unigram.clear()  
    
    return unigram


def eprint (s,clear=True):
    if clear:
        sys.stderr.write ('\x1b[K')
    sys.stderr.write (s + "\n")
    sys.stderr.flush ()


def train_phrase(iters, threshold, minfreq, uni_dict_txt, bi_dict_txt, uni_dict_bin, bi_dict_bin, file_input, file_output):
    eprint ('computing phrases: threshold = %g minfreq = %d' % (threshold,minfreq))
    filein = file_input    
    for iter in range(1,iters+1):
        eprint ('pass [%d/%d]..' % (iter,iters))
        # count n-grams
        eprint ('- computing phrases..')
        unigram = count_unigram (filein, uni_dict_txt, uni_dict_bin)
        bigram  = count_bigram  (filein, bi_dict_txt, bi_dict_bin)
        phrases = compute_phrase (unigram, bigram, threshold, minfreq)
        # save intermediate file
        if iter == iters:
            fileout = file_output
        else:
            fileout = tempfile.mktemp()
        eprint ('- writing output..')
        parse_write (filein, phrases, fileout)
        if (filein != file_input):
            os.remove (filein)
        filein = fileout
    eprint ('done.')


def read_dict (fileDICT):
    try:
        with open(fileDICT, 'rb') as input_file:
            dictionary = pickle.load(input_file)
            input_file.close()
            
    except FileNotFoundError:
        print('Dictionary file', fileDICT, ' not found!')
    return dictionary


def phrase_segmentation(threshold, minfreq, uni_dict_bin, bi_dict_bin, input, output):
    eprint ('computing phrases: threshold = %g minfreq = %d' % (threshold,minfreq))
    filein = input    

    eprint ('phrase segmentation...')
    eprint ('- read unigram dictionary')
    unigram = read_dict(uni_dict_bin)
    
    #print(unigram)
    eprint ('- read bigram dictionary')    
    bigram = read_dict(bi_dict_bin)
    #print(bigram)
    eprint ('- computing phrases..')    
    phrases = compute_phrase (unigram, bigram, threshold, minfreq)
    #print(phrases)
        # save intermediate file
    fileout = output

    print ('- writing output..., filename: ', output)
    parse_write (filein, phrases, fileout)
    #if (filein != input):
    #    os.remove (filein)
    filein = output    
    eprint ('done.')
    



sys.setrecursionlimit(10**6)

global P_unigram
global P_bigram

def read_dict (fileDICT):
    try:
        with open(fileDICT, 'rb') as input_file:
            dictionary = pickle.load(input_file)
            input_file.close()
    except FileNotFoundError:
        print('Dictionary file', fileDICT, ' not found!')
    return dictionary

class ProbDist(dict):
    ### Probability distribution estimated from unigram/bigram data
    def __init__(self, datafile=None, unigram=True, N=102490):
    #def __init__(self, datafile=None, unigram=True, N=1024908267229):
    #def __init__(self, datafile=None, unigram=True, N=8199266137832):
        #data = {}
        data = read_dict(datafile)
        for k, c in data.items():
            self[k] = self.get(k, 0) + c

        if unigram:
            self.unknownprob = lambda k, N: 10/(N*10**len(k))    # avoid unknown long word
        else:
            self.unknownprob = lambda k, N: 1/N

        self.N = N

    def __call__(self, key):
        if key in self:
            return self[key]/self.N
        else:
            return self.unknownprob(key, self.N)


def conditionalProb(word_curr, word_prev):
    ### Conditional probability of current word given the previous word.
    try:
        return P_bigram[word_prev + ' ' + word_curr]/P_unigram[word_prev]
    except KeyError:
        return P_unigram(word_curr)


@functools.lru_cache(maxsize=2**10)
#maxlen=20
def viterbi(text, prev='<S>', maxlen=20):
    if not text:
        return 0.0, []
    
    #print("text: ", text)
    textlen = min(len(text), maxlen)
    splits = [(text[:i + 1], text[i + 1:]) for i in range(textlen)]

    candidates = []
    #print("clear candidates!  candidates = []")
    for first_word, remain_word in splits:
        #pdb.set_trace()
        first_prob = math.log10(conditionalProb(first_word, prev))
        #print("first_prob of condProb(", first_word, ", ", prev, "): ", first_prob )
        remain_prob, remain_word = viterbi(remain_word, first_word)
        #print("remain_prob: ", remain_prob, ", remain_word: ", remain_word)
        candidates.append((first_prob + remain_prob, [first_word] + remain_word))
        #print("first_prob: ", str(first_prob), ", remain_prob: ", remain_prob, ", [first_word]:", [first_word], ", remain_word: ", remain_word)
        #print("Candidates: ", candidates)
        
    #print("max(candidates): " + str(max(candidates)))
    #print("====================")
    return max(candidates)

HF_myWord_DICT_REPO = "hf://LULab/myNLP-Tokenization/Models/dict_ver1"


class SyllableTokenizer:
    """
    Syllable Tokenizer using Sylbreak for Myanmar language.
    """

    def __init__(self) -> None:
        self._my_consonant = r"က-အ"
        self._en_char = r"a-zA-Z0-9"
        self._other_char = r"ဣဤဥဦဧဩဪဿ၌၍၏၀-၉၊။!-/:-@\[-`{-~\s"
        self._ss_symbol = "္"
        self._a_that = "်"
        pattern = (
            rf"((?<!.{self._ss_symbol})["  # negative‑lookbehind for stacked consonant
            rf"{self._my_consonant}"       # any Burmese consonant
            rf"](?![{self._a_that}{self._ss_symbol}])"  # not followed by virama
            rf"|[{self._en_char}{self._other_char}])"
        )
        self._break_pattern: re.Pattern[str] = re.compile(pattern)

    def tokenize(self, raw_text: str) -> List[str]:
        """Return a list of syllables for *raw_text*."""
        lined_text = re.sub(self._break_pattern, r" \1", raw_text)
        return lined_text.split()


class WordTokenizer:
    """
    Word Tokenizer using myWord (Viterbi + n-gram probability).
    """

    def __init__(self) -> None:
        # Download pre-trained binary dictionary files
        self.unigram_word_bin = cached_path(f"{HF_myWord_DICT_REPO}/unigram-word.bin")
        self.bigram_word_bin = cached_path(f"{HF_myWord_DICT_REPO}/bigram-word.bin")

        # Load probability distributions
        P_unigram = ProbDist(self.unigram_word_bin, True)
        P_bigram = ProbDist(self.bigram_word_bin, False)

    def tokenize(self, raw_text: str) -> List[str]:
        _, tokens = viterbi(raw_text.replace(" ", "").strip())
        return tokens


class PhraseTokenizer(WordTokenizer):
    """
    NPMI-based Phrase Tokenizer (using myWord segmenter as base).
    """

    def __init__(self, threshold: float = 0.1, minfreq: int = 2) -> None:
        self.unigram_phrase_bin = cached_path(f"{HF_myWord_DICT_REPO}/unigram-phrase.bin")
        self.bigram_phrase_bin = cached_path(f"{HF_myWord_DICT_REPO}/bigram-phrase.bin")
        self.threshold = threshold
        self.minfreq = minfreq
        super().__init__()

    def tokenize(self, raw_text: str) -> List[str]:
        unigram = read_dict(self.unigram_phrase_bin)
        bigram = read_dict(self.bigram_phrase_bin)
        phrases = compute_phrase(unigram, bigram, self.threshold, self.minfreq)
        words = super().tokenize(raw_text)
        if not words:
            return []
        return collocate(words, phrases)