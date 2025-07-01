"""
Humanities Integration: Literature, Philosophy, History, Linguistics, Cultural Studies
"""
import nltk
from nltk import FreqDist

class HumanitiesModule:
    def analyze_text(self, text):
        tokens = nltk.word_tokenize(text)
        fdist = FreqDist(tokens)
        return fdist.most_common(10)
