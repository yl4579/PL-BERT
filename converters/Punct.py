
from singleton_decorator import singleton

@singleton
class Punct:
    """
    Steps:
    - 1 Return the token raw, no changes made

    Note:
    Punctuation always stays the same
    """
    def __init__(self):
        super().__init__()
    
    def convert(self, token: str) -> str:
        # 1 Return the token raw, no changes made
        return token
