
from singleton_decorator import singleton

import re, os

from .Cardinal import Cardinal
from .Digit import Digit

@singleton
class Money:
    """
    Steps:
    - 1 Remove commas and spaces
    - 2 Try to match a decimal of roughly the form x.y
    - 3 Otherwise, try to match an integer
    - 4 Check the text before the number for a currency
    - 5 Check after for currency and or suffixes
      - 5.1 Match from start of after, no case, to try and find suffixes like "thousand", "million", "bn"
      - 5.2 Match from start of after, no case, try to find currencies
    - 6 If there is decimal support for the currency, and no scale ("thousand", "million", etc.),
        then output should be like "x euro y cents ..."
    - 7 Otherwise, output should be like "x point y ..."
    - 8 Finally, append a potential remaining suffix

    Some potential cases:
        $0.15            -> fifteen cents
        $1.56            -> one dollar and fifty six cents
        $77,208          -> seventy seven thousand two hundred eight dollars
        £50              -> fifty pounds
        US$75,000        -> seventy five thousand dollars
        INR 3,858 crore  -> three thousand eight hundred fifty eight crore indian rupees
        INR 31,000 crore -> thirty one thousand crore indian rupees
        14 trillion won  -> fourteen trillion won
        BEF44            -> forty four belgian francs
        RS 1000          -> one thousand rupees
        NT$1.83 billion  -> one point eight three billion dollars
        2016 dollars     -> two thousand sixteen dollars
        €3.5 million     -> three point five million euros
        ¥6,000,000       -> six million yen
        9,500,000USD     -> nine million five hundred thousand united states dollars
        - Note the difference between dollars and united states dollars
        16 DM            -> sixteen german marks
        Rs 10 lakh       -> ten lakh rupees
        400 DKK          -> four hundred danish kroner
        NOK 750,000      -> seven hundred fifty thousand norwegian kroner
        1 billion yen    -> one billion yen
        A$18.5 million   -> eighteen point five million dollars
        1.8 million yuan -> one point eight million yuan
        CA$1.7 million   -> one point seven million dollars
        Rs.12.83 crore   -> twelve point eight three crore rupees
        Rs.6299          -> six thousand two hundred ninety nine rupees
        DKK 1.03         -> one danish krone and three ore

        Potential bn/m/billion etc suffix
        Potential "INR x crore"
        Dollars, pounds

    Missed cases:
        BSD -> "billion sd"
        Before                                    Correct                                   Predicted
        2005 MKMF                               2005 MKMF   two thousand five million comorian francs
        386BSD  three hundred eighty six bahamian dollars         three hundred eighty six billion sd
        CYP2E1                                     CYP2E1                       two cypriot pounds e1
        CYP2E1                                     CYP2E1                       two cypriot pounds e1
        PHP 5.1    five philippine pesos and ten centavos             five point one philippine pesos
        2.50 DM       two german marks and fifty pfennigs               two point five o german marks
        4.2BSD     four bahamian dollars and twenty cents                   four point two billion sd
        LTL150        one hundred fifty lithuanian litass          one hundred fifty lithuanian litai
        DKK 1.03           one danish krone and three ore             one point o three danish kroner

    """
    def __init__(self):
        super().__init__()
        # Regex to detect input of the sort "x.y" or ".y"
        self.decimal_regex = re.compile(r"(.*?)(-?\d*)\.(\d+)(.*)")
        # Regex to detect a number
        self.number_regex = re.compile(r"(.*?)(-?\d+)(.*)")
        # Regex filter to remove commas and spaces
        self.filter_regex = re.compile(r"[, ]")

        # Suffixes for currencies with decimal support
        # In a perfect world this dict would contain all currencies
        self.currencies = {
            "$": {
                "number":{
                    "singular": "dollar",
                    "plural":   "dollars"
                },
                "decimal":{
                    "singular": "cent",
                    "plural":   "cents"
                }
            },
            "usd": {
                "number":{
                    "singular": "united states dollar",
                    "plural":   "united states dollars"
                },
                "decimal":{
                    "singular": "cent",
                    "plural":   "cents"
                }
            },
            "€": {
                "number":{
                    "singular": "euro",
                    "plural":   "euros"
                },
                "decimal":{
                    "singular": "cent",
                    "plural":   "cents"
                }
            },
            "£": {
                "number":{
                    "singular": "pound",
                    "plural":   "pounds"
                },
                "decimal":{
                    "singular": "penny",
                    "plural":   "pence"
                }
            }
        }

        # Suffixes for currencies
        with open(os.path.join(os.path.dirname(__file__), "money.json"), "r") as f:
            import json
            self.currencies = {**json.load(f), **self.currencies}

        # List of potential suffixes
        self.suffixes = [
            "lakh",
            "crore",
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

        # Dict of abbreviated suffixes, or other suffixes that need transformations
        self.abbr_suffixes = {
            "k": "thousand",
            "m": "million",
            "bn": "billion",
            "b": "billion",
            "t": "trillion",
            
            "cr": "crore",
            "crores": "crore",
            "lakhs": "lakh",
            "lacs": "lakh"
        }

        # Regular expression to detect the suffixes
        #self.suffix_regex = re.compile(f"({'|'.join( sorted(self.suffixes + list(self.abbr_suffixes.keys()), key=len, reverse=True) )})(.*)", flags=re.I)
        self.suffix_regex = re.compile(f"(quattuordecillion|septendecillion|novemdecillion|quindecillion|octodecillion|tredecillion|sexdecillion|vigintillion|quadrillion|quintillion|undecillion|sextillion|septillion|octillion|thousand|trillion|million|billion|crores|crore|lakhs|lakh|lacs|bn|cr|k|m|b|t)(.*)", flags=re.I)
        
        # Instead of using a regex generated using self.decimal_currencies and self.number_currencies, a manual version is used, as the generated version uses unescaped "." and "$".
        #self.suffix_regex = re.compile(r"(quattuordecillion|septendecillion|novemdecillion|quindecillion|octodecillion|tredecillion|sexdecillion|vigintillion|quadrillion|quintillion|undecillion|sextillion|septillion|octillion|thousand|trillion|million|billion|crores|crore|lakhs|lakh|lacs|bn|cr|k|m|b|t)")
        self.currency_regex = re.compile(r"(.*?)(dollar|usd|rs\.|r\$|aed|afn|all|amd|ang|aoa|ars|aud|awg|azn|bam|bbd|bdt|bgn|bhd|bif|bmd|bnd|bob|brl|bsd|btc|btn|bwp|byn|bzd|cad|cdf|chf|clf|clp|cnh|cny|cop|crc|cuc|cup|cve|czk|djf|dkk|dop|dzd|egp|ern|etb|eur|fjd|fkp|gbp|gel|ggp|ghs|gip|gmd|gnf|gtq|gyd|hkd|hnl|hrk|htg|huf|idr|ils|imp|inr|iqd|irr|isk|jep|jmd|jod|jpy|kes|kgs|khr|kmf|kpw|krw|kwd|kyd|kzt|lak|lbp|lkr|lrd|lsl|lyd|mad|mdl|mga|mkd|mmk|mnt|mop|mro|mru|mur|mvr|mwk|mxn|myr|mzn|nad|ngn|nio|nok|npr|nzd|omr|pab|pen|pgk|php|pkr|pln|pyg|qar|ron|rsd|rub|rwf|sar|sbd|scr|sdg|sek|sgd|shp|sll|sos|srd|ssp|std|stn|svc|syp|szl|thb|tjs|tmt|tnd|top|try|ttd|twd|tzs|uah|ugx|usd|uyu|uzs|vef|vnd|vuv|wst|xaf|xag|xau|xcd|xdr|xof|xpd|xpf|xpt|yer|zar|zmw|zwl|fim|bef|cyp|ats|ltl|zl|u\$s|rs|tk|r$|dm|\$|€|£|¥)(.*?)", flags=re.I)

        # Cardinal and Digit conversion
        self.cardinal = Cardinal()
        self.digit = Digit()

    def convert(self, token: str) -> str:

        # 1 Remove commas and spaces
        token = self.filter_regex.sub("", token)

        # Before and After track sections before and after a number respectively
        before = ""
        after = ""
        
        # Currency will be a dict for the currency
        currency = None

        # Number represents x in "x.y" or "x", while number represents y
        number = ""
        decimal = ""

        # Scale represents the numerical scale, eg "million" or "lakh"
        scale = ""

        # 2 Try to match a decimal of roughly the form x.y
        # Match the reverse so the regex "anchors" around the last dot instead of the first.
        # This helps with cases such as "Rs.12.38".
        match = self.decimal_regex.search(token[::-1])
        if match:
            # If there is a match, store what appears before and after the match
            # as well as the number and decimal values.
            before = match.group(4)[::-1]
            number = match.group(3)[::-1]
            decimal = match.group(2)[::-1]
            after = match.group(1)[::-1]
        
        else:
            # 3 Otherwise, try to match an integer
            match = self.number_regex.search(token)
            if match:
                before = match.group(1)
                number = match.group(2)
                after = match.group(3)
        
        # 4 Check the text before the number for a currency
        if before:
            before = before.lower()
            if before in self.currencies:
                currency = self.currencies[before]
            elif before[-1] in self.currencies:
                currency = self.currencies[before[-1]]

        # 5 Check after for currency and or suffixes
        if after:
            # 5.1 Match from start of after, no case, to try and find suffixes like "thousand", "million", "bn"
            # TODO: Reverse order and check currencies before suffixes like k
            match = self.suffix_regex.match(after)
            if match:
                scale = match.group(1).lower()
                scale = self.abbr_suffixes[scale] if scale in self.abbr_suffixes else scale
                after = match.group(2)

            # 5.2 Match from start of after, no case, try to find currencies
            if after.lower() in self.currencies:
                currency = self.currencies[after.lower()]
                after = ""

        # Decimal_support tracks whether the current currency supports decimal values
        # for "one euro and fifteen cents" instead of "one point fifteen euro"
        decimal_support = currency and "number" in currency

        result_list = []
        if decimal_support and not scale:
            # 6 If the current currency has decimal support and there is no scale like million, 
            # then we want to output like "x euro y cents"

            # Only output number if:
            # Number exists and
            #   Number is not 0
            #   OR
            #   Number is 0 but there is no decimal
            if number and (number != "0" or not decimal):
                result_list.append(self.cardinal.convert(number))
                result_list.append(currency["number"]["singular" if number == "1" else "plural"])
                if decimal and decimal != "0" * len(decimal):
                    result_list.append("and")
            # If a decimal exists and it's not just 0's, then pad it to length 2 and add the cardinal representation of the value
            # plus the text representation of the decimal, eg "cents"
            if decimal and decimal != "0" * len(decimal):
                # Pad decimal to length 2. "5" -> "50"
                decimal = f"{decimal:0<2}"
                result_list.append(self.cardinal.convert(decimal))
                result_list.append(currency["decimal"]["singular" if decimal == "01" else "plural"])
        
        else:
            # 7 Is there is a scale or no decimal support, output should be like "one point two million dollars"
            if number:
                result_list.append(self.cardinal.convert(number))
            if decimal and decimal != "0" * len(decimal):
                result_list.append("point")
                result_list.append(self.digit.convert(decimal))
            # If "million" exists:
            if scale:
                result_list.append(scale)
            # Add currency
            if currency:
                # Ensure currency is of the form {'singular': '...', 'plural': '...'}
                if decimal_support:
                    currency = currency["number"]
                # Add the currency in singular when these conditions apply
                if number == "1" and not decimal and not scale:
                    result_list.append(currency["singular"])
                else:
                    result_list.append(currency["plural"])
        
        # 8 Append a potentially remaining "after"
        if after:
            result_list.append(after.lower())

        # Convert list of values into the final result
        result = " ".join(result_list)

        return result
