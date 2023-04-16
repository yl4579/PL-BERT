
from singleton_decorator import singleton

import re

@singleton
class Verbatim:
    """
    Steps:
    - 1 If token occurs in the translation dict for eg. greek symbols, return that
    - 2 Otherwise, if the token is just one character, but not in the translation dict, return it
    - 3 Otherwise, for each character, map it to the correct format, and place spaces between all results from the map
      - Note that the correct format translates eg 6 to "s i x", which is somewhat surprising.

    Edge Cases:
    "#" -> "number" (accounts for 94.986% of cases)
    "#" -> "hash"   (accounts for  5.014% of cases)
    
    Note:
    ".6-cM" -> "dot s i x d a s h c m"
    Interestingly, a dash becomes "d a s h", while a dot becomes "dot". 
    Also, numbers are converted to cardinals and then each character is space padded.
    Kind of strange, honestly.

    Missed Cases:
    "florida" -> "florida" 
    Occurs a surprising 53 times, breaking the rules that you would expect from something of the "VERBATIM" class.
    The same can be found with "nevada" and "minnesota".
    
    "#" is always converted to "number".
    
    "20033" -> "two o o three three" 
    19 times a 5 character digit is converted via digit rules according to the data, 
    rather than via the verbatim rules (where 6 -> "s i x")
    """
    def __init__(self):
        super().__init__()

        # Translation dict from some single characters to text
        self.trans_dict = {
            # Words
            "feet": "feet",

            # Characters
            "&": "and",
            "_": "underscore",
            "#": "number",
            "€": "euro",
            "$": "dollar",
            "£": "pound",
            "~": "tilde",
            "%": "percent",

            # Math related
            "²": "squared",
            "³": "cubed",
            "×": "times",
            "=": "equals",
            ">": "greater than",

            # Greek
            "α": "alpha",
            "Α": "alpha",
            "β": "beta",
            "Β": "beta",
            "γ": "gamma",
            "Γ": "gamma",
            "δ": "delta",
            "Δ": "delta",
            "ε": "epsilon",
            "Ε": "epsilon",
            "ζ": "zeta",
            "Ζ": "zeta",
            "η": "eta",
            "Η": "eta",
            "θ": "theta",
            "Θ": "theta",
            "ι": "iota",
            "Ι": "iota",
            "κ": "kappa",
            "Κ": "kappa",
            "λ": "lambda",
            "Λ": "lambda",
            "Μ": "mu",
            "μ": "mu",
            "ν": "nu",
            "Ν": "nu",
            "ξ": "xi",
            "Ξ": "xi",
            "ο": "omicron",
            "Ο": "omicron",
            "π": "pi",
            "Π": "pi",
            "ρ": "rho",
            "Ρ": "rho",
            "ς": "sigma",
            "σ": "sigma",
            "Σ": "sigma",
            "Ϲ": "sigma",
            "ϲ": "sigma",
            "τ": "tau",
            "Τ": "tau",
            "υ": "upsilon",
            "Υ": "upsilon",
            "φ": "phi",
            "Φ": "phi",
            "χ": "chi",
            "Χ": "chi",
            "ψ": "psi",
            "Ψ": "psi",
            "ω": "omega",
            "Ω": "omega",

            # Measurement
            "µ": "micro"
        }

        # Translation dict for converting numbers to the desired format, 
        # without having to use the Cardinal conversion.
        # Includes . -> "dot" for convenience.
        self.trans_ordinal_dict = {
            ".": "dot",
            "-": "d a s h",

            "0": "o",
            "1": "o n e",
            "2": "t w o",
            "3": "t h r e e",
            "4": "f o u r",
            "5": "f i v e",
            "6": "s i x",
            "7": "s e v e n",
            "8": "e i g h t",
            "9": "n i n e"
        }

    def convert(self, token: str) -> str:
        # 1 If token occurs in the translation dict for eg. greek symbols, return that
        if token in self.trans_dict:
            return self.trans_dict[token]

        # 2 If the token is just one character, but not in the translation dict, return it
        # This preserves uppercase versus the next option
        if len(token) == 1:
            return token

        # 3 For each character, map it to the correct format, and place spaces between all results from the map
        return " ".join([self.convert_char(c) for c in token])

    def convert_char(self, char: str) -> str:
        # If the character exists in the translation dict
        if char in self.trans_ordinal_dict:
            return self.trans_ordinal_dict[char]

        # If the character exists in the secondary translation dict
        if char in self.trans_dict:
            return self.trans_dict[char]

        # Otherwise return the lowercase of the character
        return char.lower()
