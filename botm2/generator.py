from random import randint, choice
import sys
from tkinter import DISABLED, NORMAL




class TextGenerator:
    def __init__(self, words, n=2):
        self.words = words
        upper_words = set()
        for word in words:
            if word[0].isupper():
                upper_words.add(word)
        self.upper_words = list(sorted(upper_words))
        self.text = list()
        self.n = n

    def add_word(self):
        if not self.text:
            word = self.get_upper()
        elif len(self.text) <= self.n:
            word = self.get_word(len(self.text))
        else:
            word = self.get_word(self.n)
        if word:
            self.text.append(word)
            return word
        else:
            return False

    def get_upper(self):
        return self.upper_words[randint(0, len(self.upper_words)-1)]

    def get_word(self, n):
        indexies = []
        phrase = self.text[len(self.text) - n:]
        # for i, j in enumerate(self.words[:-n]):
        #     if self.words[i:i+n] == phrase:
        #         indexies.append(i+n)
        # return self.words[choice(indexies)]
        word_index = 0
        while True:
            try:
                word_index = self.words.index(
                    phrase[0], word_index, len(self.words) - 1)
            except ValueError:
                break
            else:
                if self.words[word_index: word_index + n] == phrase:
                    indexies.append(word_index + n)
                word_index += 1
                if word_index > len(self.words) - (n+1):
                    break
        try:
            i = choice(indexies)
            return self.words[i]
        except IndexError:
            return self.get_upper()

    def generate_text(self):
        while True:
            new_word = self.add_word()
            yield new_word
        full_text = ' '.join(self.text)
        return full_text
