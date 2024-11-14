
class Color:
    def __init__(self):
        self.RED = "red"
        self.GREEN = "green"
        self.BLUE = "blue"
        self.YELLOW = "yellow"

        self.VALUES = [self.RED, self.GREEN, self.BLUE, self.YELLOW]


class Special:
    def __init__(self):
        self.REVERSE = "reverse"
        self.SKIP = "skip"
        self.WILD = "wild"
        self.WILDPLUSTWO = "wildplustwo"
        self.WILDPLUSFOUR = "wildplusfour"

        self.VALUES = [self.REVERSE, self.SKIP, self.WILD, self.WILDPLUSTWO, self.WILDPLUSFOUR]

class Colors:
    def __init__(self):
        self.red = (234, 29, 37);
        self.green = (46, 204, 113);
        self.black = (0, 0, 0);

        self.uno_blue = (52, 152, 219);
        self.uno_green = (46, 204, 113);
        self.uno_red = (231, 76, 60);
        self.uno_yellow = (241, 196, 15);


Color = Color()
Special = Special()
Colors = Colors() # The naming is kinda confusing (Color is for the card object, but Colors is for discord? and has RGB values)

if __name__ == "__main__":
    pass