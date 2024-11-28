
from CONSTANTS import Color, Special, Colors # Or you could do import *
import random


class Card:
    def __init__(self, **kwargs):
        self.color = None
        self.number = None
        self.special = None

        if len(kwargs) == 0:
            self.create_random_card()
        elif set(kwargs.keys()) == ("color", "number"):
            self.create_card(color=kwargs["color"], number=kwargs["number"])
        elif set(kwargs.keys()) == ("color", "special"):
            self.create_card(color=kwargs["color"], special=kwargs["special"])
        elif set(kwargs.keys()) == ("special"):
            self.create_card(special=kwargs["special"])
        else:
            raise Exception(f"Couldn't create a card, invalid arguments: {kwargs}")

    def __str__(self) -> str:
        if self.color is not None and self.number is not None:
            return f"{self.color} {self.number}"
        elif self.color is not None and self.special is not None:
            return f"{self.color} {self.special}"
        elif self.special is not None:
            return f"{self.special}"
        else:
            return f"Unknown card: Number - {self.number}, Color - {self.color}, Special - {self.special}"

    def create_random_card(self) -> None:
        self.color = Color.VALUES[random.randint(0, len(Color.VALUES) - 1)]
        self.number = random.randint(0, 14)

        # Bigger than 9 means that it is a special card
        if self.number > 9:
            self.special = Special.VALUES[self.number - 10]
            
            # If it is a color change or +4
            if self.special == Special.WILD or self.special == Special.WILDPLUSFOUR:
                self.color = None

            self.number = None

    def create_card(self, color=None, number=None, special=None) -> None:
        self.color = color
        self.number = number
        self.special = special

    def get_discord_color(self) -> tuple[int]:
        """Get the RGB value for this card."""
        match self.color:
            case Color.RED:
                return Colors.uno_red
            case Color.GREEN:
                return Colors.uno_green
            case Color.BLUE:
                return Colors.uno_blue
            case Color.YELLOW:
                return Colors.uno_yellow
            case _: # Default case
                return Colors.black
            
    def get_color_emoji(self) -> str:
        """Get emoji for discord i would guess."""
        match self.color:
            case Color.RED:
                return "🟥"
            case Color.GREEN:
                return "🟩"
            case Color.BLUE:
                return "🟦"
            case Color.YELLOW:
                return "🟨"
            case _: # Default case
                return "🎨"
            
            
    def get_special_emoji(self) -> None | str:
        if self.special == Special.REVERSE:
            return "🔃"
        elif self.special == Special.SKIP:
            return "🚫"
        return None


if __name__ == "__main__":
    
    # Basically testing if the randomness is random enough, so make 1_000_000 cards
    cards = [Card() for _ in range(1_000_000)]
    
    ratios = {}
    
    for card in cards:
        if card.number is not None and card.color and not card.special:
            if (card.color, card.number) in ratios:
                ratios[(card.color, card.number)] += 1
            else:
                ratios[(card.color, card.number)] = 1
            continue
        
        elif card.color and card.special and not card.number:
            if (card.color, card.special) in ratios:
                ratios[(card.color, card.special)] += 1
            else:
                ratios[(card.color, card.special)] = 1
            continue
        
        elif card.special and not card.color and not card.number:
            if card.special in ratios:
                ratios[card.special] += 1
            else:
                ratios[card.special] = 1
            continue
        
        else: print(f"unknown card: {card}")
        
    # Wild and wildplusfour have 4 times the average amount, because they don't have a color
    for card in sorted(ratios.items(), key= lambda a: -a[1]): # Sort the card frequencies in reverse
        print(card)
                
                
        