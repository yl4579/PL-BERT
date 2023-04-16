
from singleton_decorator import singleton

import re

from .Cardinal import Cardinal

@singleton
class Fraction:
    """
    Steps:
    - 1 Filter out commas
    - 2 Check whether we the input consists for example ½
    - 3 If it does, get the text representing the unicode character
    - 4 If it does, check whether there are remaining values (eg in the case of 8 ½)
    - 5 If it does have remaining values, convert those remaining values to Cardinal style and prepend them
    - 6 Try to match values of the format .../...
    - 7 Get the numerator and denominator of the match.
    - 8 Strip the numerator and denominator of spaces
    - 9 Turn the numerator into cardinal style
    - 10 Test the denominator for edge cases such as "1", "2" and "4"
    - 11 If no such edge cases apply, convert the denominator to cardinal style, 
         and replace the last word with a word in the -th or -ths style.
    - 12 Get the potential remaining values (eg in 2 1/2)
    - 13 Turn these values to cardinal, prepend them to the result, and potentially changing "one" to "a".

    Special Cases:
    ½, ¼, ¾, ⅔, ⅛, ⅞, ⅝, etc.
    1½ -> one and a half
    ½  -> one half
    8 1/2 -> 8 and a half
    1/4 -> one quarter
    4/1 -> four over one
    100 000/24 -> one hundred thousand twenty fourths

    Note:
    Always has either a "x y/z", "x/y", "½", or "8 ½"
    """
    def __init__(self):
        super().__init__()
        # Regex to filter out commas
        self.filter_regex = re.compile(",")
        # Regex to filter out spaces
        self.space_filter_regex = re.compile(" ")
        # Translation dict for special cases
        self.trans_dict = {
            "½": {
                "prepended": "a",
                "single": "one",
                "text": "half"
                },
            "⅓": {
                "prepended": "a",
                "single": "one",
                "text": "third"
                },
            "⅔": {
                "prepended": "two",
                "single": "two",
                "text": "thirds"
                },
            "¼": {
                "prepended": "a",
                "single": "one",
                "text": "quarter"
                },
            "¾": {
                "prepended": "three",
                "single": "three",
                "text": "quarters"
                },
            "⅕": {
                "prepended": "a",
                "single": "one",
                "text": "fifth"
                },
            "⅖": {
                "prepended": "two",
                "single": "two",
                "text": "fifths"
                },
            "⅗": {
                "prepended": "three",
                "single": "three",
                "text": "fifths"
                },
            "⅘": {
                "prepended": "four",
                "single": "four",
                "text": "fifths"
                },
            "⅙": {
                "prepended": "a",
                "single": "one",
                "text": "sixth"
                },
            "⅚": {
                "prepended": "five",
                "single": "five",
                "text": "sixths"
                },
            "⅐": {
                "prepended": "a",
                "single": "one",
                "text": "sixth"
                },
            "⅛": {
                "prepended": "an",
                "single": "one",
                "text": "eighth"
                },
            "⅜": {
                "prepended": "three",
                "single": "three",
                "text": "eighths"
                },
            "⅝": {
                "prepended": "five",
                "single": "five",
                "text": "eighths"
                },
            "⅞": {
                "prepended": "seven",
                "single": "seven",
                "text": "eighths"
                },
            "⅑": {
                "prepended": "a",
                "single": "one",
                "text": "ninth"
                },
            "⅒": {
                "prepended": "a",
                "single": "one",
                "text": "tenth"
                }
        }
        # Regex to check for special case
        self.special_regex = re.compile(f"({'|'.join(self.trans_dict.keys())})")
        self.cardinal = Cardinal()

        # Regex for .../...
        # The simpler version of this regex does not allow for "100 000/24" to be seen as "100000/24"
        #self.slash_regex = re.compile(r"(-?\d+) */ *(-?\d+)")
        self.slash_regex = re.compile(r"(-?\d{1,3}( \d{3})+|-?\d+) *\/ *(-?\d{1,3}( \d{3})+|-?\d+)")

        # Translation from Cardinal style to Ordinal style
        self.trans_denominator = {
            "zero": "zeroth",
            "one": "first",
            "two": "second",
            "three": "third",
            "four": "fourth",
            "five": "fifth",
            "six": "sixth",
            "seven": "seventh",
            "eight": "eighth",
            "nine": "ninth",

            "ten": "tenth",
            "twenty": "twentieth",
            "thirty": "thirtieth",
            "forty": "fortieth",
            "fifty": "fiftieth",
            "sixty": "sixtieth",
            "seventy": "seventieth",
            "eighty": "eightieth",
            "ninety": "ninetieth",

            "eleven": "eleventh",
            "twelve": "twelfth",
            "thirteen": "thirteenth",
            "fourteen": "fourteenth",
            "fifteen": "fifteenth",
            "sixteen": "sixteenth",
            "seventeen": "seventeenth",
            "eighteen": "eighteenth",
            "nineteen": "nineteenth",

            "hundred": "hundredth",
            "thousand": "thousandth",
            "million": "millionth",
            "billion": "billionth",
            "trillion": "trillionth",
            "quadrillion": "quadrillionth",
            "quintillion": "quintillionth",
            "sextillion": "sextillionth",
            "septillion": "septillionth",
            "octillion": "octillionth",
            "undecillion": "undecillionth",
            "tredecillion": "tredecillionth",
            "quattuordecillion": "quattuordecillionth",
            "quindecillion": "quindecillionth",
            "sexdecillion": "sexdecillionth",
            "septendecillion": "septendecillionth",
            "octodecillion": "octodecillionth",
            "novemdecillion": "novemdecillionth",
            "vigintillion": "vigintillionth"
        }

        # Translation dict for edge cases
        self.edge_dict = {
            "1": {
                "singular": "over one",
                "plural": "over one"
                },
            "2": {
                "singular": "half",
                "plural": "halves"
                },
            "4":{
                "singular": "quarter",
                "plural": "quarters"
                }
        }

    def convert(self, token: str) -> str:
        # 1 Filter commas and dots, but keep spaces
        token = self.filter_regex.sub("", token)
        # 2 Check for special unicode case
        match = self.special_regex.search(token)
        if match:
            # 3 Get fraction match from first group
            frac = match.group(1)
            frac_dict = self.trans_dict[frac]

            # 4 Check whether remainder contains a number, eg in "1½"
            remainder = self.special_regex.sub("", token)
            # 5 If it does, convert it using the Cardinal convertion: "1202" -> "one thousand two hundred two"
            if remainder:
                prefix = self.cardinal.convert(remainder)
                result = f"{prefix} and {frac_dict['prepended']} {frac_dict['text']}"
            else:
                result = f"{frac_dict['single']} {frac_dict['text']}"
        
        else:
            # 6 Match .../... as two groups
            match = self.slash_regex.search(token)
            if match:
                # 7 Get the numerator and denominators from the groups
                numerator = match.group(1)
                denominator = match.group(3)
                
                # 8 Strip the numerator and denominator of spaces
                numerator = self.space_filter_regex.sub("", numerator)
                denominator = self.space_filter_regex.sub("", denominator)

                # 9 The numerator is a number in cardinal style
                numerator_text = self.cardinal.convert(numerator)

                # 10 We have some edge cases to deal with
                if denominator in self.edge_dict:
                    # Apply edge cases
                    result = f"{numerator_text} {self.edge_dict[denominator][('singular' if abs(int(numerator)) == 1 else 'plural')]}"
                
                else:
                    # 11 Convert the denominator to cardinal style, and convert the last word to
                    # the denominator style using self.trans_denominator.
                    denominator_text_list = self.cardinal.convert(denominator).split(" ")
                    denominator_text_list[-1] = self.trans_denominator[denominator_text_list[-1]]
                    # Potentially add "s" if the numerator is larger than 1.
                    # eg ninth -> ninths 
                    if abs(int(numerator)) != 1:
                        denominator_text_list[-1] += "s"
                    denominator_text = " ".join(denominator_text_list)
                    result = f"{numerator_text} {denominator_text}"
                
                # 12 Get remaining values
                remainder = self.slash_regex.sub("", token)
                if remainder:
                    # 13 Transform remaining values to cardinal
                    remainder_text = self.cardinal.convert(remainder)
                    # Potentially transform "one" to "a" if possible
                    result_list = result.split()
                    if result_list[0] == "one":
                        result_list[0] = "a"
                    # Prepend the remaining values in cardinal style
                    result = f"{remainder_text} and {' '.join(result_list)}"
            
            else:
                # Unhandled case. Should not occur if token really is of the FRACTION class
                result = token

        return result
