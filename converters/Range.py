
from singleton_decorator import singleton
import re
from .Cardinal import Cardinal

@singleton
class Range:
    """
    Steps:
    - Check for - splitting numbers

    Note:
    Punctuation always stays the same
    """
    def __init__(self, language='en'):
        super().__init__()
        self.cardinal = Cardinal()
        self.language = language
    
    def convert(self, token: str) -> str:
        numbers = re.split('-', token)
        if len(numbers) == 1 : 
            token = self.cardinal.convert(numbers[0])
        elif len(numbers) == 2 : 

            if self.language == 'ml' :   
                token = self.cardinal.convert(numbers[0])
                token += ' മുതൽ  '
                token += self.cardinal.convert(numbers[1])
                token += ' വരെ   '
            else : 
                token = self.cardinal.convert(numbers[0])
                token += ' to '
                token += self.cardinal.convert(numbers[1])

        else : 
            token = ''
            for number in numbers :    
                token += self.cardinal.convert(number)
                token += ' '

        return token
