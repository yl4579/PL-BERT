
from singleton_decorator import singleton

import re

from .Cardinal import Cardinal
from .Digit import Digit

@singleton
class Address:
    """
    Steps:
    - 1 Strip spaces from token
    - 2 Try to match some "letters-numbers" or "letters numbers"
      - 2.1 Add the letter part either as a word or as an abbreviation (eg verbatim)
      - 2.2 Add the numbers either as partially cardinal and partially digit, or as fully digit
      - 2.3 Potentially add suffix like "west" for handling the edge case

    Edge case:
    "I02W" -> "i o two west"
    """
    def __init__(self):
        super().__init__()
        # Regex to filter out spaces, dots and dashes
        self.filter_regex = re.compile(r"[. -]")
        # Regex to detect address
        self.address_regex = re.compile(r"((?P<upper_prefix>[A-Z\.]*)|(?P<lower_prefix>[a-zA-Z]*))(?P<link>( |-)*)(?P<number>\d+)(?P<suffix>N|E|S|W|n|e|s|w)?")

        # Translation dict for converting directions
        self.direction_trans_dict = {
            "n": "north",
            "e": "east",
            "s": "south",
            "w": "west",
        }

        # Cardinal and Digit conversion
        self.cardinal = Cardinal()
        self.digit = Digit()

    def convert(self, token: str) -> str:
        
        # 1 Strip spaces from token
        token = token.strip()
        
        result_list = []

        # 2 Try to match some "letters-numbers" or "letters numbers"
        match = self.address_regex.match(token)
        if match:
            # Extract values from match
            lower_prefix, upper_prefix, link, number, suffix = match.group("lower_prefix"), match.group("upper_prefix"), match.group("link"), match.group("number"), match.group("suffix")

            # 2.1 There is either a lower_prefix or an upper_prefix. 
            # lower_prefix is a word and is added as lowercase.
            # upper_prefix is all upper, and is added as an abbreviation
            if lower_prefix:
                result_list.append(lower_prefix.lower())
            elif upper_prefix:
                result_list += [c for c in upper_prefix.lower() if c != "."]

            # 2.2 We use partial cardinal conversion if number has length 2, or sometimes with length 3
            if ((link or number[-1] == "0" or number[0] == "0") and len(number) == 3) or len(number) == 2:
                if number[-3:-2]:
                    result_list.append(self.digit.convert(number[-3:-2]))
                if number[-2:-1] == "0":
                    result_list.append("o")
                    result_list.append(self.digit.convert(number[-1]))
                else:
                    result_list.append(self.cardinal.convert(number[-2:]))
            
            else:
                # Otherwise use digit conversion for number
                result_list.append(self.digit.convert(number))
            
            # If a suffix exists, and is a direction, then add the direction for edge case "I02W" -> "i o two west"
            if suffix:
                result_list.append(self.direction_trans_dict[suffix.lower()])

            return " ".join(result_list)
        
        return token
