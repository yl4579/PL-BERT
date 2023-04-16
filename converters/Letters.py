
from singleton_decorator import singleton

import re

from .Verbatim import Verbatim

@singleton
class Letters:
    """
    Steps:
    - 1 Handle the edge case of "nan"
    - 2 Consider only the first word, unless a word ends with a dot
    - 3 If the length is one, return a translation of the character, or just the character
    - 4 If the token ends with a dash, do not include a suffix
    - 5 Remove the suffix "'s" or "s" if it exists, and otherwise state that no suffix should be included in the output
    - 6 Return a string padded version of all characters, converted using Verbatim conversion

    Missed cases:
        Before                                Correct                            Predicted
        années                      a n n e acute e's                    a n n e acute e s
        québécois       q u e acute b e acute c o i's        q u e acute b e acute c o i s
        héros                         h e acute r o's                      h e acute r o s
        e.g. A                                    e g                                e g a
        Us                                        u s                                  u's

        Most of these cases include é, and are due to the difference between including or excluding the '.
    """
    def __init__(self):
        super().__init__()
        # Regex to filter out non letters and "&". Preserve accents.
        self.filter_regex = re.compile(r"[^A-Za-zÀ-ÖØ-öø-ÿ&']")
        # Match until " ", unless ". "
        self.first_word_regex = re.compile(r"")
        # Conversion for Verbatim
        self.verbatim = Verbatim()
        # Translation dict to convert accented characters properly
        self.trans_dict = {
            "é": "e acute",
        }
    
    def convert(self, token: str) -> str:
        
        # 1 If input is a float, it is "nan". This should become "n a"
        if type(token) == float:
            return "n a"
        
        # 2 Consider only the first word
        # Unless the token is of the form "x. y"
        if " " in token and ". " not in token:
            token = token.split(" ")[0]

        # 3 If the length of the token is 1, return the translation of the token, or the token itself
        if len(token) == 1:
            if token in self.trans_dict:
                return self.trans_dict[token]
            return token
        
        # Get custom suffix
        suffix = True

        # 4 Never a ' suffix if the token ended with a dash
        if token[-1] == "-":
            suffix = False

        # Remove non letters
        token = self.filter_regex.sub("", str(token))
        
        # 5 Potentiall shrink token
        if suffix and len(token) >= 3 and token[-2:] in ("'s", "s'"):
            # Shrink token if token ends with 's or s'
            token = token[:-2]
        elif suffix and token and token[-1] == "s" and any([c.isupper() for c in token[:-1]]):
            # Check for a series of uppercase followed by an "s"
            token = token[:-1]
        else:
            # Reset suffix to default if none options to add a suffix were executed
            suffix = False

        # 6 Result a string padded version of the list, while ignoring "'"
        return " ".join([self.convert_char(char) for char in token if char != "'"]) + ("'s" if suffix else "")

    def convert_char(self, char: str) -> str:
        # If the character exists in the translation dict
        if char in self.trans_dict:
            return self.trans_dict[char]

        # Otherwise return the lowercase of the character
        return self.verbatim.convert_char(char)
