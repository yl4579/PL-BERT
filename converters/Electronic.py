
from singleton_decorator import singleton

import re

from .Cardinal import Cardinal
from .Digit import Digit

@singleton
class Electronic:
    """
    Steps (data):
    - 1 Convert token to lowercase
    - 2 Handle edge case with just ::
    - 3 Handle "#Text" -> "hash tag text" edge case
    - 4 Iterate over token
      - 4.1 If the token starts with "http(s)://", and ".com" is encountered, add "dot com"
      - 4.2 Use digit or cardinal conversion to convert numbers
      - 4.3 Or add non-numeric characters using the right translation directory, 
            depending on whether the token starts with "http(s)://"

    Steps (sensible):
    - 1 Convert token to lowercase
    - 2 Handle edge case with just ::
    - 3 Handle "#Text" -> "hash tag text" edge case
    - 4 Iterate over token
      - 4.1 If ".com" is encountered, add "dot com"
      - 4.2 Convert character using sensible translation dictionary

    Edge case:
    "::" -> "::"
    rather than "colon colon"
    "#Text" -> "hash tag text"

    """
    def __init__(self):
        super().__init__()
        # Translation dict for URL sections
        self.data_https_dict = {
            "/": "slash",
            ":": "colon",
            ".": "dot",
            "#": "hash",
            "-": "dash",

            "é": "e a c u t e",
            
            # Somehow these should be said like this, according to the data
            "(": "o p e n i n g p a r e n t h e s i s",
            ")": "c l o s i n g p a r e n t h e s i s",
            "_": "u n d e r s c o r e",
            ",": "c o m m a",
            "%": "p e r c e n t",
            "~": "t i l d e",
            ";": "s e m i colon",
            "'": "s i n g l e q u o t e",
            "\"": "d o u b l e q u o t e",

            "0": "o",
            "1": "o n e",
            "2": "t w o",
            "3": "t h r e e",
            "4": "f o u r",
            "5": "f i v e",
            "6": "s i x",
            "7": "s e v e n",
            "8": "e i g h t",
            "9": "n i n e",
        }

        # Translation dict for urls without http(s) at the start
        self.data_no_https_dict = {
            "/": "s l a s h",
            ":": "c o l o n",
            ".": "dot",
            "#": "h a s h",
            "-": "d a s h",

            "é": "e a c u t e",
            
            "(": "o p e n i n g p a r e n t h e s i s",
            ")": "c l o s i n g p a r e n t h e s i s",
            "_": "u n d e r s c o r e",
            ",": "c o m m a",
            "%": "p e r c e n t",
            "~": "t i l d e",
            ";": "s e m i c o l o n",
            "'": "s i n g l e q u o t e",
            "\"": "d o u b l e q u o t e",
            
            "0": "o",
            "1": "o n e",
            "2": "t w o",
            "3": "t h r e e",
            "4": "f o u r",
            "5": "f i v e",
            "6": "s i x",
            "7": "s e v e n",
            "8": "e i g h t",
            "9": "n i n e",
        }

        # Regex to test for "https?://"
        self.data_http_regex = re.compile(r"https?://")
        
        # Translation dict for sensible conversion
        self.sensible_trans_dict = {
            "/": "slash",
            ":": "colon",
            ".": "dot",
            "#": "hash",
            "-": "dash",
            "é": "e acute",
            "(": "opening parenthesis",
            ")": "closing parenthesis",
            "_": "underscore",
            ",": "comma",
            "%": "percent",
            "~": "tilde",
            ";": "semicolon",
            "'": "single quote",
            "\"": "double quote",

            "0": "zero",
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

        # Cardinal and digit conversion
        self.cardinal = Cardinal()
        self.digit = Digit()

    def convert(self, token: str) -> str:
        # 1 Convert to lowercase
        token = token.lower()

        # 2 Check for edge case with just ::
        if token == "::":
            return token

        # 3 Check for #Text -> "hash tag text"
        if token[0] == "#" and len(token) > 1:
            return self.convert_hash_tag(token)

        # Variable stating whether token starts with http(s)://
        # If the string starts with http(s)://, then we use "dot com"
        # If the string does not start with http(s)://, then we use "dot c o m", 
        # and generate space-pad everything except "dot"
        http = self.data_http_regex.match(token) != None
        # Get the translation dict to use for this token
        data_trans_dict = self.data_https_dict if http else self.data_no_https_dict
        
        result_list = []
        c_index = 0
        while c_index < len(token):
            if http:
                # 4.1 If .com, add "dot com"
                if token[c_index:].startswith(".com"):
                    result_list.append("dot com")
                    c_index += len(".com")
                    continue
            
            # Get the amount of subsequent numbers starting from this index
            offset = 0
            while c_index + offset < len(token) and token[c_index + offset].isdigit():
                offset += 1
            
            # 4.2 Either use cardinal or digit conversion for representing the numbers
            if offset == 2 and token[c_index] != "0":
                text = self.cardinal.convert(token[c_index:c_index + offset])
                result_list.append(" ".join([c for c in text if c != " "]))
                c_index += offset
            elif offset > 0 and token[c_index] != "0" * offset:
                text = self.digit.convert(token[c_index:c_index + offset])
                result_list.append(" ".join([c for c in text if c != " "]))
                c_index += offset
            else:
                # 4.3 Or add non-numeric character either passed through a translation dictionary,
                # or just the character
                if token[c_index] in data_trans_dict:
                    result_list.append(data_trans_dict[token[c_index]])
                else:
                    result_list.append(token[c_index])                    
                c_index += 1

        return " ".join(result_list)
    
    # This conversion actually makes sense, and would be useful, in contrast to the one used in the data
    def sensible_convert(self, token: str) -> str:
        # 1 Convert to lowercase
        token = token.lower()

        # 2 Check for edge case with just ::
        if token == "::":
            return token

        # 3 Check for "#Text" -> "hash tag text"
        if token[0] == "#" and len(token) > 1:
            return self.convert_hash_tag(token)

        result_list = []
        c_index = 0
        while c_index < len(token):
            # 4.1 If ".com" is encountered, add "dot com"
            if token[c_index:].startswith(".com"):
                result_list.append("dot com")
                c_index += 4
                continue
            
            # 4.2 Convert character using sensible translation dictionary
            char = token[c_index]
            if char in self.sensible_trans_dict:
                result_list.append(self.sensible_trans_dict[char])
            else:
                result_list.append(char)

            c_index += 1
        
        return " ".join(result_list)
    
    def convert_hash_tag(self, token: str) -> str:
        # Parse the hash tag message
        out = "hash tag "
        for char in token[1:].lower():
            if char in self.sensible_trans_dict:
                if out[-1] == " ":
                    out += self.sensible_trans_dict[char] + " "
                else:
                    out += " " + self.sensible_trans_dict[char] + " "
            else:
                out += char
        return out.strip()
