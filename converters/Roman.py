
from singleton_decorator import singleton

import re

@singleton
class Roman:
    """
    Steps:
    - 1 Get largest section
    - 2 Check for suffix 's
    - 3 Apply strict filtering
    - 4 Calculate total value of roman numeral in integers
    - 5 Return string representation of total, as well as the suffix

    Special cases:
    II I -> two
    IIs  -> two's
    II.  -> two
    """
    def __init__(self):
        super().__init__()
        # Regex out non-roman numerals
        self.roman_filter_strict_regex = re.compile("[^IVXLCDM]")
        # Regex to detect roman numerals
        self.roman_filter_regex = re.compile(r"[.IVXLCDM]+(th|nd|st|rd|'s|s)?")
    
        # Roman Numeral value dict
        self.roman_numerals = {
            "I": 1,
            "V": 5,
            "X": 10,
            "L": 50,
            "C": 100,
            "D": 500,
            "M": 1000
        }

    def convert(self, token: str) -> (str, str):
        # 1 Split the token in sections and work with the largest one, in case the input is "I II"
        token = max(token.split(" "), key=len)

        # 2 Check whether we need to use the suffix "'s"
        suffix = ""
        if token[-1:] == "s":
            suffix = "'s"
        
        # 3 Apply strict filtering to remove ".", "'" and "s"
        token = self.roman_filter_strict_regex.sub("", token)

        # 4 We loop over the token in reverse, constantly either adding or subtracting the value represented
        # by the character, based on previous tokens. 
        total = 0
        prev = 0
        for c in reversed(token):
            cur = self.roman_numerals[c]
            total += cur if cur >= prev else -cur
            prev = cur
        
        # 5 Convert the integer to a string so other converters can use the value 
        return (str(total), suffix)
    
    def check_if_roman(self, token: str) -> bool:
        # Check whether the largest section of the token is deemed a roman numeral
        return self.roman_filter_regex.fullmatch(max(token.split(" "), key=len)) != None
