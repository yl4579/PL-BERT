
from singleton_decorator import singleton

import re

@singleton
class Telephone:
    """
    Steps:
    - 1 Convert to lowercase and replace parentheses with dashes
    - 2 Convert each character in the token
    - 3 Remove multiple "sil"'s in a row. Also remove "sil" at the start.
    - 4 Replace subsequent "o"s with "hundred" or "thousand" where applicable

    Note:
    Telephone contains 0-9, "-", a-z, A-Z, " ", "(", ")"
    1 case with dots too: 527-28479 U.S. -> five two seven sil two eight four seven nine
    2 cases with commas too: 116-20, RCA, -> one one six sil two o sil r c a
                             2 1943-1990, -> two sil one nine four three sil one nine nine o
    Data is not 100% accurate: 15-16 OCTOBER 1987 -> one five sil one six sil october sil one nine eight seven

    Missed cases:
    Difference between abbreviations and words:
    "53-8 FNB MATIES" -> "five three sil eight sil f n b sil maties"
              instead of "five three sil eight sil f n b sil m a t i e s"
    """
    def __init__(self):
        super().__init__()
        # Translation dict
        self.trans_dict = {
            " ": "sil",
            "-": "sil",

            "x": "extension",

            "0": "o",
            "1": "one",
            "2": "two",
            "3": "three",
            "4": "four",
            "5": "five",
            "6": "six",
            "7": "seven",
            "8": "eight",
            "9": "nine",
        }
        # Regex to filter out parentheses
        self.filter_regex = re.compile(r"[()]")

    def convert(self, token: str) -> str:
        # 1 Convert to lowercase and replace parentheses with dashes
        token = self.filter_regex.sub("-", token.lower())

        # 2 Convert list of characters
        result_list = [self.trans_dict[c] if c in self.trans_dict else c for c in token]

        # 3 Remove multiple "sil"'s in a row. Also remove "sil" at the start.
        result_list = [section for i, section in enumerate(result_list) if section != "sil" or (i - 1 >= 0 and result_list[i - 1] != "sil")]

        # 4 Iterate over result_list and replace multiple "o"s in a row with "hundred" or "thousand", 
        # but only if preceded with something other than "o" or "sil", and if succeeded with "sil" or the end of the list.
        i = 0
        while i < len(result_list):
            offset = 0
            while i + offset < len(result_list) and result_list[i + offset] == "o":
                offset += 1

            if (i + offset >= len(result_list) or result_list[i + offset] == "sil") and (i - 1 < 0 or result_list[i - 1] not in ("o", "sil")) and offset in (2, 3):
                result_list[i : offset + i] = ["hundred"] if offset == 2 else ["thousand"]

            i += 1

        return " ".join(result_list)
