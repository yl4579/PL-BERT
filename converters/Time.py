
from singleton_decorator import singleton

import re

from .Cardinal import Cardinal

@singleton
class Time:
    """
    Steps:
    - 1 Strip the token to remove extra spaces
    - 2 Try to match "hh.mm (pm)"
      - 2.1 Add the hour, potentially roughly modulo 12
      - 2.2 Add the minute if it exists and is not 00
      - 2.3 Add "hundred" or "o'clock" if minute is not added
      - 2.4 Prepend the suffix, eg pm
    - 3 Otherwise, try to match "(hh:)mm:ss(.ms) (pm)"
      - 3.1 If hour, add it as cardinal and add "hour" with proper plurality
      - 3.2 If minute, add it as cardinal and add "minute" with proper plurality
      - 3.3 If seconds, add "and" if seconds is the last number, add seconds as cardinal, and "second" with proper plurality
      - 3.4 If milliseconds, add "and", milliseconds as cardinal, and "millisecond" with proper plurality
      - 3.5 If suffix, prepend the suffix with padded spaces
    - 4 Otherwise, try to match "xxH", eg. "PM3"
      - 2.1 Add the hour, potentially roughly modulo 12
    
    Edge case:
    "PM2" -> "two p m"
    """
    def __init__(self):
        super().__init__()

        # Regex to filter out dots
        self.filter_regex = re.compile(r"[. ]")
        # Regex to detect time in the form xx:yy (pm)
        self.time_regex = re.compile(r"^(?P<hour>\d{1,2}) *((?::|.) *(?P<minute>\d{1,2}))? *(?P<suffix>[a-zA-Z\. ]*)$", flags=re.I)
        # Regex to detect time in the form xx:yy:zz
        self.full_time_regex = re.compile(r"^(?:(?P<hour>\d{1,2}) *:)? *(?P<minute>\d{1,2})(?: *: *(?P<seconds>\d{1,2})(?: *. *(?P<milliseconds>\d{1,2}))?)? *(?P<suffix>[a-zA-Z\. ]*)$", flags=re.I)
        # Regex to detect time in the form AM5 and PM7
        self.ampm_time_regex = re.compile(r"^(?P<suffix>[a-zA-Z\. ]*)(?P<hour>\d{1,2})", flags=re.I)

        # Cardinal conversion
        self.cardinal = Cardinal()

    def convert(self, token: str) -> str:

        # 1 Strip the token to remove extra spaces
        token = token.strip()

        result_list = []

        # 2 Try to match "hh.mm (pm)"
        match = self.time_regex.match(token)
        if match:
            # Extract hour, minute and suffix from the match
            hour, minute, suffix = match.group("hour"), match.group("minute"), match.group("suffix")

            # Boolean to track whether the time is suffixed with "am" or "pm"
            ampm = self.filter_regex.sub("", suffix).lower().startswith(("am", "pm"))

            # 2.1 If ampm is prepended, we say "one p m" when hour is "13", but "thirteen" if there is no "pm" or "am"
            if ampm:
                result_list.append(self.cardinal.convert(self.modulo_hour(hour)))
            else:
                result_list.append(self.cardinal.convert(hour))

            # 2.2 Add the minute if it exists and is not just zeros
            if minute and minute != "00":
                if minute[0] == "0":
                    result_list.append("o")
                result_list.append(self.cardinal.convert(minute))

            elif not ampm:
                # 2.3 If there is no minute, add either "hundred" or "o'clock", unless "pm" exists. 
                # Eg "12:00 pm" -> "twelve p m", without "hundred" or "o'clock"
                if int(hour) > 12 or int(hour) == 0:
                    result_list.append("hundred")
                else:
                    result_list.append("o'clock")

            # 2.4 Prepend the suffix with padded spaces
            if suffix:
                result_list += [c for c in suffix.lower() if c not in (" ", ".")]
            
            return " ".join(result_list)

        # 3 Try to match "(hh:)mm:ss(.ms) (pm)"
        match = self.full_time_regex.match(token)
        if match:
            # Extract values from match
            hour, minute, seconds, milliseconds, suffix = match.group("hour"), match.group("minute"), match.group("seconds"), match.group("milliseconds"), match.group("suffix")

            # 3.1 If hour, add it as cardinal and add "hour" with proper plurality
            if hour:
                result_list.append(self.cardinal.convert(hour))
                result_list.append("hour" if int(hour) == 1 else "hours")
            # 3.2 If minute, add it as cardinal and add "minute" with proper plurality
            if minute:
                result_list.append(self.cardinal.convert(minute))
                result_list.append("minute" if int(minute) == 1 else "minutes")
            # 3.3 If seconds, add "and" if seconds is the last number, add seconds as cardinal, and "second" with proper plurality
            if seconds:
                if not milliseconds:
                    result_list.append("and")
                result_list.append(self.cardinal.convert(seconds))
                result_list.append("second" if int(seconds) == 1 else "seconds")
            # 3.4 If milliseconds, add "and", milliseconds as cardinal, and "millisecond" with proper plurality
            if milliseconds:
                result_list.append("and")
                result_list.append(self.cardinal.convert(milliseconds))
                result_list.append("millisecond" if int(milliseconds) == 1 else "milliseconds")
            # 3.5 If suffix, prepend the suffix with padded spaces
            if suffix:
                result_list += [c for c in suffix.lower() if c not in (" ", ".")]
            
            return " ".join(result_list)
        
        # 4 Try to match "xxH", eg. "PM3"
        match = self.ampm_time_regex.match(token)
        if match:
            # Extract values from match
            hour, suffix = match.group("hour"), match.group("suffix")

            # Boolean to track whether the time is suffixed with "am" or "pm"
            ampm = self.filter_regex.sub("", suffix).lower().startswith(("am", "pm"))

            # 4.1 If ampm is prepended, we say "one p m" when hour is "13", but "thirteen" if there is no "pm" or "am"
            if ampm:
                result_list.append(self.cardinal.convert(self.modulo_hour(hour)))
            else:
                result_list.append(self.cardinal.convert(hour))
            result_list += [c for c in suffix.lower() if c not in (" ", ".")]
            return " ".join(result_list)

        return token

    def modulo_hour(self, hour: str) -> str:
        # "12pm" -> "twelve p m", while "1pm" -> "one p m"
        if hour == "12":
            return hour
        return str(int(hour) % 12)
