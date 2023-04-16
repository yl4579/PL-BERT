
from singleton_decorator import singleton

import re

from .Digit import Digit
from .Cardinal import Cardinal

@singleton
class Decimal:
    """
    Steps:
    - 1 Filter out commas
    - 2 Check for the form "x.y" or ".y", and update the decimal and/or number
    - 3 Otherwise, check for the form "x" and update the numbers
    - 4 Check for "billion", "million", etc. suffix
    - 5 Otherwise, check for "xEy" suffix for the edge cases
    - 6 Add "point" to output if there is a decimal
    - 7 Add "zero" only if the decimal is "0", and there is a number in front of the dot, and there is no suffix (if there is a decimal)
    - 8 Otherwise add digit version of the decimal (if there is a decimal)
    - 9 If there is a number, add the cardinal of it in front
    - 10 Add the suffix in front, if one exists
 
    Edge cases:
    3.66E-49 -> three point six six times ten to the minus fourty nine
    """
    def __init__(self):
        super().__init__()
        # Regex to detect input of the sort "x.y" or ".y"
        self.decimal_regex = re.compile(r"(-?\d*)\.(\d+)(.*)")
        # Regex to detect a number
        self.number_regex = re.compile(r"(-?\d+)(.*)")
        # Regex filter to remove commas
        self.filter_regex = re.compile(r"[,]")
        # Digit and Cardinal conversion
        self.cardinal = Cardinal()
        self.digit = Digit()
        # List of potential suffixes
        self.suffixes = [
            "thousand", 
            "million", 
            "billion", 
            "trillion", 
            "quadrillion", 
            "quintillion", 
            "sextillion", 
            "septillion", 
            "octillion", 
            "undecillion", 
            "tredecillion", 
            "quattuordecillion", 
            "quindecillion", 
            "sexdecillion", 
            "septendecillion", 
            "octodecillion", 
            "novemdecillion", 
            "vigintillion"
        ]
        # Regular expression to detect the suffixes
        self.suffix_regex = re.compile(f" *({'|'.join(self.suffixes)})")
        # Regular expression for xEy
        self.e_suffix_regex = re.compile(r" *E(-?\d+)")
    
    def convert(self, token: str) -> str:

        # 1 Filter out commas
        token = self.filter_regex.sub("", token)

        # Variable to store values from the input string
        number = ""
        decimal = ""

        # 2 Check for the form x.y
        match = self.decimal_regex.match(token)
        if match:
            # Get the values before and after the dot
            number = match.group(1)
            decimal = match.group(2)
            # Update token to remove the decimal
            token = match.group(3)

        else:
            match = self.number_regex.match(token)
            if match:
                # 3 Get the number, and update the token to the remainder
                number = match.group(1)
                token = match.group(2)

        # 4 Match suffix, eg billion
        match = self.suffix_regex.match(token)
        suffix = ""
        if match:
            suffix = match.group(1)
        else:
            # 5 Otherwise, try to match xEy
            match = self.e_suffix_regex.match(token)
            if match:
                # Turn the suffix into "times ten to the y"
                suffix = f"times ten to the {self.cardinal.convert(match.group(1))}"

        # Make list for output
        result_list = []
        # 6, 7 Only if the decimal is 0, and there is a number in front of the dot, and there is no suffix
        # then we use "zero" instead of "o".
        if len(decimal) > 0:
            result_list.append("point")
            if decimal == "0" and len(number) > 0 and len(suffix) == 0:
                result_list.append("zero")
            else:
                # 8 Otherwise use Digit conversion
                result_list.append(self.digit.convert(decimal))

        # 9 If there is a number (there doesn't have to be), then add it in front
        if number:
            result_list.insert(0, self.cardinal.convert(number))

        # 10 Add the suffix if applicable
        if suffix:
            result_list.append(suffix)

        # 11 Number may be empty. In this case, avoid it.
        result = " ".join(result_list)
        
        return result
