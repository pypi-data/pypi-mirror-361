import re
from typing import List
from cached_path import cached_path

import word_segment as wseg
import phrase_segment as phr

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
        wseg.P_unigram = wseg.ProbDist(self.unigram_word_bin, True)
        wseg.P_bigram = wseg.ProbDist(self.bigram_word_bin, False)

    def tokenize(self, raw_text: str) -> List[str]:
        _, tokens = wseg.viterbi(raw_text.replace(" ", "").strip())
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
        unigram = phr.read_dict(self.unigram_phrase_bin)
        bigram = phr.read_dict(self.bigram_phrase_bin)
        phrases = phr.compute_phrase(unigram, bigram, self.threshold, self.minfreq)
        words = super().tokenize(raw_text)
        if not words:
            return []
        return phr.collocate(words, phrases)