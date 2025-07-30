

class DiffEmptyException(Exception):
    def __init__(self, message:str="No changes found in staged files."):
        self.message = message
        super().__init__(self.message)