
from singleton_decorator import singleton

import re, os

@singleton
class Plain:
    """
    Steps:
    - 1 Check for "NaN" edge case
    - 2 Check whether the token with preserved capitalisation matches the translation dictionary
    - 3 Check whether token mapped to lowercase matches the translation dictionary
    - 4 Remove all non-digit and non-letter characters
    - 5 Split on "strasse". This is the only often occurring case where extra spaces should be added

    Strange cases:
        "Jan", "Feb" and "Mar" are not converted to "january", "february" and "march" respectively, 
        while the other months of the year are converted to their full counterparts. 
        I've opted to convert all months completely.

        Some names, such as "Elisabeth" and "Isaak" are normalized and converted to "elizabeth" and "izaak". I've opted not to support this.

        Sometimes tokens like "NO" are converted to chemistry terms like "nitrogen monoxide". I've opted not to support this.
    
    There are 3 "plain.json" files, each with slightly different uses. The one currently being used is one trained very specifically
    on the training data.
    """
    def __init__(self):
        super().__init__()
        # Translation dict for uppercase, full messages
        self.upper_trans_dict = {
            "DR": "drive", # Also often "Doctor"
            "ST": "street"
        }

        # Translation dict for converting full messages
        self.trans_dict = {
        }

        # Get data from plain.json file with common UK -> US text conversion
        with open(os.path.join(os.path.dirname(__file__), "plain.json")) as f:
            import json
            self.trans_dict = {**self.trans_dict, **json.load(f)}

        # List of items to split at
        self.split_at = [
            "strasse",
            "weg",
        ]

        # Regex to detect where to split
        self.split_at_regex = re.compile(f"(.*)({'|'.join(self.split_at)})$", flags=re.I)
    
    def convert(self, token: str) -> str:
        # 1 "NaN" might be passed, which will be considered a float
        if isinstance(token, float):
            return "NaN"
        
        # 2 Check whether the token with preserved capitalisation matches the translation dictionary
        if token in self.upper_trans_dict:
            return self.upper_trans_dict[token]

        # 3 Check whether token mapped to lowercase matches the translation dictionary
        if token.lower() in self.trans_dict:
            return self.trans_dict[token.lower()]

        # 4 Remove all non-digit and non-letter characters. Preserve diacritical marks (eg umlauts, accent grave, etc.)
        token = re.sub(r"[^a-zA-ZÀ-ÖØ-öø-ÿ0-9']", "", token)

        # 5 If the token ends with something specific the string should split at,
        # Use a regex to detect the location of the split, and convert to lowercase
        if token.lower().endswith(tuple(self.split_at)):
            groups = self.split_at_regex.match(token).groups()
            # Only if the first group is nonempty do we turn the result to lowercase
            if groups[0]:
                token = " ".join(groups).lower()

        return token
