class Printer:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    END = '\033[0m'
    BOLD = '\033[1m'

    @classmethod
    def print(cls, text, colour=BLUE, end='\n'):
        print(colour + text + cls.END, end=end)
