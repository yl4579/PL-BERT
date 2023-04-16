
from singleton_decorator import singleton

import re

from .Decimal import Decimal
from .Fraction import Fraction

@singleton
class Measure:
    """
    Steps:
    - 1 Filter out commas
    - 2 Try to match a fraction
      - 2.1 If possible, use Fraction convertor
    - 3 Otherwise, try to match "x.y" or "x"
      - 3.1 If possible, use Decimal convertor
    - 4 Iterate over chunks of the remainder, the actual measure
      - 4.1 Try to match with a dictionary while preserving case sensitivity
      - 4.2 Otherwise try to match with a dictionary while ignoring case sensitivity
      - 4.3 Otherwise add the chunk itself to the output
            Note that plurality of the measures is kept track of
    - 5 Handle the edge case where "cubic centimeter" is written as "c c"

    Edge case:
    All cases of "cm3" are converted to "c c" rather than "cubic centimeter"

    Missed Cases:
        Before          "Correct"                                   Predicted
        1/2 kg          half a kilogram                             one half of a kilogram
        7.62 mm M       seven point six two millimeters             seven point six two millimeters meters
        57m             fifty seven minutes                         fifty seven meters
        2.3Kb           two point three kilobits                    two point three kilobytes
    
    Differences between my predictions and "Correct" values:
        Lack of spaces:
            Before          "Correct"                                   Predicted
            100mA           one hundred milli amperes                   one hundred milliamperes
            200mA           two hundred milli amperes                   two hundred milliamperes
            135 KC          one hundred thirty five kilo coulombs       one hundred thirty five kilocoulombs
            97Gs            ninety seven giga seconds                   ninety seven gigaseconds
            ...             ...                                         ...
            Note that several hundred of these occurrences exist within the training data.
        
        Incorrect measure on the data's side:
            Before          "Correct"                                   Predicted
            13.0 pH         thirteen point zero pico henrys             thirteen point zero p h

        No translation on the data's side:
            Before          "Correct"                                   Predicted
            30 million km   30 million km                               thirty million kilometers
            549 KiB         549 KiB                                     five hundred forty nine kibibytes
            1.60 MiB        1.60 MiB                                    one point six o mebibytes
            1000/year       one thousand per years                      one thousand per year
            ...             ...                                         ...
            Note that several dozens of these occurrences exist within the training data.
    """
    def __init__(self):
        super().__init__()
        # Regex to detect fraction
        self.fraction_regex = re.compile(r"(((?:-?\d* )?-?\d+ *\/ *-? *\d+)|(-?\d* *(?:½|⅓|⅔|¼|¾|⅕|⅖|⅗|⅘|⅙|⅚|⅐|⅛|⅜|⅝|⅞|⅑|⅒)))")
        # Regex to detect whether "of a" should be used. Matches only when "of a" should NOT be used
        self.of_a_regex = re.compile(r"(-?\d+ -?\d+ *\/ *-? *\d+)|(-?\d+ *(?:½|⅓|⅔|¼|¾|⅕|⅖|⅗|⅘|⅙|⅚|⅐|⅛|⅜|⅝|⅞|⅑|⅒))")
        # Regex to detect input to pass to digit convertor, including potential million/billion suffix
        self.value_regex = re.compile(r"(-?(?: |\d)*\.?\d+ *(?:thousand|million|billion|trillion|quadrillion|quintillion|sextillion|septillion|octillion|undecillion|tredecillion|quattuordecillion|quindecillion|sexdecillion|septendecillion|octodecillion|novemdecillion|vigintillion)?)")
        # Regex filter to remove commas
        self.filter_regex = re.compile(r"[,]")
        # Regex filter to remove spaces
        self.filter_space_regex = re.compile(r"[ ]")
        # Regex to remove letters
        self.letter_filter_regex = re.compile(r"[^0-9\-\.]")

        # Prefix dict for 10^i with i > 0
        # Prefix dict
        self.prefix_dict = {
            "Y": "yotta",
            "Z": "zetta",
            "E": "exa",
            "P": "peta",
            "T": "tera",
            "G": "giga",
            "M": "mega",
            "k": "kilo",
            "h": "hecto",
            "da": "deca",
            "d": "deci",
            "c": "centi",
            "m": "milli",
            "μ": "micro",
            "µ": "micro", # legacy symbol. 
            "n": "nano",
            "p": "pico",
            "f": "femto",
            "a": "atto",
            "z": "zepto",
            "y": "yocto"
        }

        # Translation dict for prefixable measure types. 
        # These will get prefixed with 
        self.prefixable_trans_dict = {
            "m": {
                "singular": "meter",
                "plural": "meters"
            },
            "b": {
                "singular": "bit", # Note that this messes with byte whenever the lowercase is used
                "plural": "bits"
            },
            "B": {
                "singular": "byte",
                "plural": "bytes"
            },
            "bps": {
                "singular": "bit per second", # Note that this messes with byte whenever the lowercase is used
                "plural": "bits per second"
            },
            "Bps": {
                "singular": "byte per second",
                "plural": "bytes per second"
            },
            "g": {
                "singular": "gram",
                "plural": "grams"
            },
            "gf": {
                "singular": "gram force",
                "plural": "grams force"
            },
            "W": {
                "singular": "watt",
                "plural": "watts"
            },
            "Wh": {
                "singular": "watt hour",
                "plural": "watt hours"
            },
            "Hz": {
                "singular": "hertz",
                "plural": "hertz"
            },
            "hz": {
                "singular": "hertz",
                "plural": "hertz"
            },
            "J": {
                "singular": "joule",
                "plural": "joules"
            },
            "L": {
                "singular": "liter",
                "plural": "liters"
            },
            "V": {
                "singular": "volt",
                "plural": "volts"
            },
            "f": {
                "singular": "farad",
                "plural": "farads"
            },
            "s": {
                "singular": "second",
                "plural": "seconds"
            },
            "A": {
                "singular": "ampere",
                "plural": "amperes"
            },
            "Ah": {
                "singular": "amp hour",
                "plural": "amp hours"
            },
            "Pa": {
                "singular": "pascal",
                "plural": "pascals"
            },
            "s": {
                "singular": "second",
                "plural": "seconds"
            },
            "C": {
                "singular": "coulomb",
                "plural": "coulombs"
            },
            "Bq": {
                "singular": "becquerel",
                "plural": "becquerels"
            },
            "N": {
                "singular": "newton",
                "plural": "newtons"
            },
            "bar": {
                "singular": "bar",
                "plural": "bars"
            },
            "lm": { # TODO: This turns "Klm" -> "kilolumens", while Kilometer may have been intended?
                "singular": "lumen",
                "plural": "lumens"
            },
            "cal": {
                "singular": "calorie",
                "plural": "calories"
            },
        }

        # Transformed prefixed dict using self.prefixable_trans_dict and the dict of prefixes
        self.prefixed_dict = {prefix + prefixed: {"singular": self.prefix_dict[prefix] + self.prefixable_trans_dict[prefixed]["singular"], "plural": self.prefix_dict[prefix] + self.prefixable_trans_dict[prefixed]["plural"]} for prefixed in self.prefixable_trans_dict for prefix in self.prefix_dict}
        self.prefixed_dict = {**self.prefixed_dict, **self.prefixable_trans_dict}

        # Translation dict for non-prefixed measure types
        # Also overrides values from self.prefixed_dict, like "mb" -> "millibyte"
        self.custom_dict = {
            "%": {
                "singular": "percent",
                "plural": "percent"
            },
            "pc": {
                "singular": "percent",
                "plural": "percent"
            },
            "ft": {
                "singular": "foot",
                "plural": "feet"
            },
            "mi": {
                "singular": "mile",
                "plural": "miles"
            },
            "mb": {
                "singular": "megabyte",
                "plural": "megabytes"
            },
            "ha": {
                "singular": "hectare",
                "plural": "hectares"
            },
            "\"": {
                "singular": "inch",
                "plural": "inches"
            },
            "in": {
                "singular": "inch",
                "plural": "inches"
            },
            "\'": {
                "singular": "foot",
                "plural": "feet"
            },
            "rpm": {
                "singular": "revolution per minute",
                "plural": "revolutions per minute" # on "per x", x is always singular
            },
            "hp": {
                "singular": "horsepower",
                "plural": "horsepower"
            },
            "cc": {
                "singular": "c c",
                "plural": "c c"
            },
            "oz": {
                "singular": "ounce",
                "plural": "ounces",
            },
            "mph": {
                "singular": "mile per hour",
                "plural": "miles per hour"
            },
            "lb": {
                "singular": "pound",
                "plural": "pounds"
            },
            "lbs": {
                "singular": "pounds", # Always plural due to how "lbs" itself is already plural
                "plural": "pounds"
            },
            "kt": {
                "singular": "knot",
                "plural": "knots"
            },
            "dB": {
                "singular": "decibel",
                "plural": "decibels"
            },
            "AU": {
                "singular": "astronomical unit",
                "plural": "astronomical units"
            },
            "st": {
                "singular": "stone",
                "plural": "stone" # Stone is always singular, eg "nine stone"
            },
            "yd": {
                "singular": "yard",
                "plural": "yards"
            },
            "yr": {
                "singular": "year",
                "plural": "years"
            },
            "yrs": {
                "singular": "year", #TODO Consider years as "yrs" is already plural
                "plural": "years"
            },
            "eV": {
                "singular": "electron volt",
                "plural": "electron volts"
            },
            "/": {
                "singular": "per",
                "plural": "per"
            },
            "sq": {
                "singular": "square",
                "plural": "square"
            },
            "2": {
                "singular": "square",
                "plural": "square"
            },
            "²": {
                "singular": "square",
                "plural": "square"
            },
            "3": {
                "singular": "cubic",
                "plural": "cubic"
            },
            "³": {
                "singular": "cubic",
                "plural": "cubic"
            },
            "h": {
                "singular": "hour",
                "plural": "hours"
            },
            "hr": {
                "singular": "hour",
                "plural": "hours"
            },
            "hrs": {
                "singular": "hour", # TODO: Consider plural as "hrs" is already plural
                "plural": "hours"
            },
            "ch": {
                "singular": "chain",
                "plural": "chains"
            },
            "KiB": {
                "singular": "kibibyte",
                "plural": "kibibytes"
            },
            "MiB": {
                "singular": "mebibyte",
                "plural": "mebibytes"
            },
            "GiB": {
                "singular": "gibibyte",
                "plural": "gibibytes"
            },
            "pH": { # The data parses "pH" as "pico henrys"
                "singular": "p h",
                "plural": "p h"
            },
            "kph": {
                "singular": "kilometer per hour",
                "plural": "kilometers per hour"
            },
            "Da": {
                "singular": "dalton",
                "plural": "daltons"
            },
            "cwt": {
                "singular": "hundredweight",
                "plural": "hundredweight"
            },
            "Sv": {
                "singular": "sievert",
                "plural": "sieverts",
            },
            "C": { # Overrides Coulomb
                "singular": "celcius", 
                "plural": "celcius"
            },
            "degrees": {
                "singular": "degree",
                "plural": "degrees"
            },
            "degree": {
                "singular": "degree",
                "plural": "degrees"
            },
            "atm": {
                "singular": "atmosphere",
                "plural": "atmospheres"
            },
            "min": {
                "singular": "minute",
                "plural": "minutes"
            },
            "cd": {
                "singular": "candela",
                "plural": "candelas"
            },
            "ly": {
                "singular": "light year",
                "plural": "light years"
            },
            "kts": {
                "singular": "knot",
                "plural": "knots"
            },
            "mol": {
                "singular": "mole",
                "plural": "moles"
            },
            "Nm": { # Overrides nanometers on the lowercase
                "singular": "newton meter",
                "plural": "newton meters"
            },
            "Ω": {
                "singular": "ohm",
                "plural": "ohms"
            },
            "bbl": {
                "singular": "barrel",
                "plural": "barrels"
            },
            "gal": {
                "singular": "gallon",
                "plural": "gallons"
            },
            "cal": { # This overides "cal" from calorie, while preserving eg "kcal". "cal" is more often used to refer to caliber than calorie I reckon, hence this entry
                "singular": "cal",
                "plural": "cal"
            }
        }
        
        # Override and add values from custom_dict to prefixed_dict
        self.prefixed_dict = {**self.prefixed_dict, **self.custom_dict}

        # Lowercase version of self.prefixed_dict
        self.lower_prefixed_dict = {key.lower(): self.prefixed_dict[key] for key in self.prefixed_dict}
        # Note, byte and bit overlap.                               Byte has preference
        # electron volts and exavolts overlap.                      Electron Volts has preference
        # hectares and hectoamperes overlap.                        Hectares has preference
        # pascals and picoamperes and petaamperers overlap.         Pascals has preference
        # mega... and milli... overlap.                             Milli... has preference
        # pico... and peta... overlap.                              Pico... has preference
        # zetta... and zepto... overlap.                            Zepto... has preference
        # yotto... and yocto... overlap.                            Yocto... has preference
        # Daltons and deciamperes overlap.                          Daltons has preference
        # More overlaps may exist

        # Special suffixes on which the total suffix should be split
        self.special_suffixes = re.compile(r"(\/|per(?!cent)|sq|2|²|3|³)")

        # Decimal and Fraction conversion
        self.decimal = Decimal()
        self.fraction = Fraction()

    def convert(self, token: str) -> str:
        # 1 Filter out commas
        token = self.filter_regex.sub("", token)
        
        result_list = []

        # Plural is false by default, as "/s" should be "per second"
        plural = False

        # 2 Try to match a fraction
        match = self.fraction_regex.match(token)
        if match:
            # 2.1 If one exists, convert to text using the Fraction convertor
            result_list.append(self.fraction.convert(match.group(0)))
            # Turn token into remainder. Because of the usage of match instead of search, the former
            # part of the next line may not be needed
            token = token[:match.span()[0]] + token[match.span()[1]:]
            
            # Filter out spaces
            token = self.filter_space_regex.sub("", token)

            # If there is a number before the fraction, eg "8 1/2" or "8 ½", then we add "of a", and keep what's behind singular
            # Otherwise, we make what's behind plural
            if self.of_a_regex.match(match.group(0)):
                plural = True
            else:
                result_list.append("of an" if token and token[0] in list("aeiou") else "of a")
            
        else:
            # 3 Try to match "x.y" or "x"
            match = self.value_regex.match(token)
            if match:
                # 3.1 Pass without spaces to decimal convertor
                result_list.append(self.decimal.convert(self.filter_space_regex.sub("", match.group(1))))
                token = token[:match.span()[0]] + token[match.span()[1]:]
                # Plural is False when the abs of the float of the decimal value is 1, and the decimal value is not of the form "1.x"
                # Otherwise it's true
                if abs(float(self.letter_filter_regex.sub("", match.group(1)))) != 1 or "." in match.group(1):
                    plural = True

        # Variable indicating whether the "per" word was just used
        # This is used for detecting plurality
        per = False
        # 4 Iterate over the remainder of the token
        for split_token in token.split(" "):
            for i, token in enumerate(self.split_token(split_token)):
                # Add the proper name of the suffix if one exists
                # Try without case sensitivity if the previous failed
                if token in self.prefixed_dict:
                    result_list.append(self.prefixed_dict[token]["plural" if plural and not per else "singular"])
                elif token.lower() in self.lower_prefixed_dict:
                    result_list.append(self.lower_prefixed_dict[token.lower()]["plural" if plural and not per else "singular"])
                else:
                    result_list.append(token)
                
                # If previous result was "per", set per to True so "singular" is used for the next word.
                # But only if "per" wasn't the first suffix. eg "5/km2" is "five per square kilometers"
                if result_list[-1] == "per" and i != 0:
                    per = True

                # If the last word was not per, and not "square" or "cubic", reset per to False.
                # If "per" was used, followed by "square" or "cubic", we want to preserve the "singular" for
                # the upcoming word
                elif result_list[-1] not in ("square", "cubic"):
                    per = False
        
        result = " ".join(result_list)

        # 5 Handle edge case: cubic centimeter -> c c
        result = re.sub(r"cubic centimeters?", "c c", result)

        return result
    
    def split_token(self, token: str) -> str:
        while True:
            # Find match for suffix seperator
            match = self.special_suffixes.search(token)
            if match:
                # Get start and end index of match
                s1, s2 = match.span()
                if match.group(1) in ("sq", "2", "²", "3", "³"):
                    yield token[s1:s2]
                    if token[:s1]:
                        yield token[:s1]
                else:
                    if token[:s1]:
                        yield token[:s1]
                    yield token[s1:s2]
                
                # Reduce token
                token = token[s2:]
            else:
                # If there is no match, return the remainder of the token, if nonempty
                if token:
                    yield token
                # Kill while loop
                break
