import discord.context_managers
from discord.ext import commands
from discord.ui import View, Button
import discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Mängu toimimise jaoks
from Types.Card import Card
from Types.CONSTANTS import Color, Special

# Muud moodulid
import random  # Selleks, et kaarte saaks segada


class Player:
    def __init__(self, user_id, username, avatar: discord.Asset, display_name=""):
        self.user_id = user_id
        self.username = username
        self.display_name = display_name
        self.cards = []  # kaardid jagatakse mängu algades
        self.avatar = avatar  # avatar objekt (sisaldab url-i ja muid funktsioone (nt saab pildi alla laadida jne))
        
        self.card_message_id = None

    def put_card(self, card: Card) -> Card|bool:
        if card in self.cards:
            self.cards.remove(card)
            return card
        return False

    def draw_card(self, card: Card) -> None:
        self.cards.append(card)

    def draw_cards(self, cards: list[Card]) -> None:
        self.cards += cards

    def exit_game(self) -> list[Card]:
        # Eemalda kaardid ja pane need mahakäidud kaartide kaardipakki
        cards = self.cards.copy()  # Nii igaks juhuks
        self.cards = []
        return cards
    
    def set_card_message_id(self, id):
        pass

    @property
    def avatar_url(self):
        return self.avatar.url

    # Sisseehitatud funktsioonid
    def __hash__(self):
        return self.user_id
    
    def __eq__(self, other):
        if isinstance(other, Player):
            return self.user_id == other.user_id
        elif isinstance(other, discord.Member):
            return self.user_id == other.id


class GameManager:
    def __init__(self):
        self.host = None
        self.players = []
        self.player_order = []  # Mängijate järjekord (otseselt vaja ei ole)
        self.current_turn_index = 0  # Alguses on esimene mängija host
        
        self.cards = []  # Siin hoiame kaarte
        self.used_cards = []  # Siia lähevad kasutatud / juba mängitud kaardid
        # Hiljem, kui kaardid saavad kaardipakist otsa, siis kasutatud kaardid 
        # segatakse ära ning lisatakse uuesti kaardipakki põhja.
        
        self.last_played_card = None
        self.last_player = None
        
        self.turn_order = 1  # Kui on 1, siis käib õiget pidi, kui on -1, siis käib tagurpidi

    def set_host(self, user: discord.Member):
        for player in self.players:
            if player == user:
                self.host = player
                break
        else:
            self.host = self.add_player(user)
            

    def start_game(self):
        self.current_turn_index = 0  # Määrame, et mäng algab hostiga (host on kõige esimene, kes antud mängu lisati)
        # print("Players:\n", self.players)

        # UNO pakis on:
        # + numbrikaarte: 
        #    0            - üks igat värvi
        #    1-9          - kaks igat värvi
        # + värvilisi erikaarte: 
        #    +2           - kaks igat värvi
        #    reverse      - kaks igat värvi
        #    skip         - kaks igat värvi
        # + wild-kaarte: 
        #    värvivahetus - neli tükki
        #    +4 kaart     - neli tükki
        
        for color in Color.VALUES:  # Käime läbi kõik värvid (RED, GREEN, BLUE, YELLOW)
            for number in range(0, 10):  # Valime numbrid 0-st 10-ni
                self.cards.append(Card(color=color, number=number))
            
            for number in range(1, 10):  # Valime numbrid 1-st 10-ni
                self.cards.append(Card(color=color, number=number))
                
            for special in [Special.REVERSE, Special.SKIP, Special.WILDPLUSTWO]:  # Lisa 2 igat special kaarti
                self.cards.append(Card(color=color, special=special))
                self.cards.append(Card(color=color, special=special))
            
        for special in [Special.WILD, Special.WILDPLUSFOUR]:
            for _ in range(4):  # Lisa igat värvita kaarti 4 tükki (+4 ja värvivahetus)
                self.cards.append(Card(special=special))
        
        for _ in range(10):  # Sega kaarte 10 korda (ilmselt pole vaja nii palju vaja, sest iga kord tehakse kaardipaki suurus vahetust)
            self.shuffle(self.cards)  # Sega kaardipakk ära
            
        # Jaga igale mängijale 7 kaarti
        for player in self.players:
            for _ in range(7):
                player.draw_card(self.cards.pop(0))
            print("Player cards" ,player.user_id, player.cards)
        print("Game started")

    def add_player(self, user: discord.Member) -> Player:
        player = Player(user.id, user.name, user.display_avatar, user.display_name)
        self.players.append(player)
        self.player_order.append(player)
        
        return player
    
    def remove_player(self, user: discord.Member|Player) -> bool:
        if isinstance(user, discord.Member):
            for player in self.players:
                if player == user:
                    user = player
                    break
        if isinstance(user, Player):
            if user not in self.players:
                return False
            self.players.remove(user)
            # TODO: Uuenda ka indeskti, sest kui indeks on suurem kui mängija järjekorra number, siis valitakse vale mängija
            # TODO: Eemalda player_order-ist (tegelkult pole player_order-it üldse vaja)
            return True
        return False
        
    
    def shuffle(self, cards: list) -> None:
        # Käi läbi kõik kaardid ning vaheta see kaart ära mingil suvalisel positsioonil oleva kaardiga
        first_card_index, second_card_index = 0, 0
        for first_card_index in range(len(cards)):
            while first_card_index == second_card_index: # Me tahame et alati toimuks vahetus, seega proovi niikaua kuni indeksid on erinevad ja saaks vahetada
                second_card_index = random.randint(0, len(cards) - 1)  # End is inclusive
        
            # Vaheta kaardid ära
            cards[first_card_index], cards[second_card_index] = cards[second_card_index], cards[first_card_index]
            
    def get_player_by_id(self, user_id: str) -> Player|None:
        for player in self.players:
            if player.user_id == user_id:
                return player
        return None
    
    def get_game_embed(self) -> tuple[discord.File, discord.Embed]:
        global_embed = discord.Embed()
        
        current_turn_player = self.player_order[self.current_turn_index]
        
        # Lisa viimati käidud kaardi pilt
        # image_file = discord.File("path to card image")
        # global_embed.set_thumbnail(url="attachment://[filename specifiied in image_file]")
        
        image_file = discord.File("./images/BlueReverse.png", filename="blue_reverse.png")
        global_embed.set_thumbnail(url="attachment://blue_reverse.png")  # small image at the right
        
        # Kelle kord hetkel on
        global_embed.set_author(name=f"{current_turn_player.display_name}'s turn.", icon_url=current_turn_player.avatar_url)

        # global_embed.description = f"{self.last_player.username} played {self.last_played_card}"
        global_embed.description = f"Somebody played blue reverse."

        # Mängijate nimekiri ja kelle kord nüüd käia on
        players_string = ""
        for player in self.players:
            # Kas mängija on host või tavamängija
            if player == self.host:
                players_string += ":crown: "
            else:
                players_string += ":bust_in_silhouette: "
            # Millise mängija käik hetkel on
            if player == current_turn_player:
                players_string += f"**{player.display_name}**\n"  # Tee boldiks
            else:
                players_string += f"{player.display_name}\n"
            
        players_string.strip()  # Eemalda lõpust uue rea märk
        global_embed.add_field(name="**Players:**", value=players_string)
        
        return (image_file, global_embed)
    
    def get_player_embed(self, player: Player) -> discord.Embed:
        if player not in self.players:
            return
        
        card_embed = discord.Embed(title=f"You have {len(player.cards)} card{'' if len(self.cards) == 1 else 's'}")
        
        # player_cards = ""
        # for card in player.cards:
        #     if card.color and card.number is not None:
        #         player_cards += f"{card.get_color_emoji()} {card.number}\n"
        #     elif card.color and card.special:
        #         player_cards += f"{card.get_color_emoji()} {card.get_special_emoji()}\n"
        #     else:
        #         player_cards += f"{card.special}\n"
        
        # player_cards.strip()
        cards = sorted(player.cards)
        
        cards = "\n".join(map(lambda a: str(a), cards))
        
        print(player.cards)
        # card_embed.description = player_cards
        
        card_embed.description = cards
        
        return card_embed
                


games: dict[GameManager] = {}  # Selleks, et koodi oleks lihstam muuta

class GameControlView(View):
    def __init__(self, host_id, guild_id):
        super().__init__()
        self.host_id = host_id
        self.guild_id = guild_id

    @discord.ui.button(label="Start Game", style=discord.ButtonStyle.green, custom_id="start_game")
    async def start_game_button(self, interaction: discord.Interaction, button: Button):
        game = games.get(self.guild_id)

        # Prevent non-hosts from starting the game
        if interaction.user.id != self.host_id:
            await interaction.response.send_message("Only the host can start the game!", ephemeral=True)
            return

        if not game:
            await interaction.response.send_message("No game is ongoing in this server!", ephemeral=True)
            return

        if len(game.players) < 2:
            await interaction.response.send_message("You need at least 2 players to start the game!",
                                                    ephemeral=True)
            return

        game.start_game()

        await interaction.response.send_message(f"It's {game.host.display_name}'s turn!")

        # player_info = f"{game.host.name}'s turn\n"
        
        # for index, player in enumerate(game.player_order):
        #     if index == 0:
        #         continue  # Hosti ei mainita millegipärast?
        #     player_name = f"<@{player.user_id}>"
        #     player_info += f"{player_name}: {len(player.cards)}\n"  # Mitu kaarti mängijal käes on
        #     print(player.username, len(player.cards))
        
        

        game_view = GameGameplayView(game.host.user_id, self.guild_id)

        card_file, game_state = game.get_game_embed()

        await interaction.followup.send(embed=game_state, file=card_file, view=game_view)



    @discord.ui.button(label="Join Game", style=discord.ButtonStyle.green, custom_id="join_game")
    async def join_game_button(self, interaction: discord.Interaction, button: Button):
        game = games.get(self.guild_id)
        if game:
            player_id = interaction.user.id
            if player_id not in map(lambda a: a.user_id, game.players):
                game.add_player(interaction.user)

                if interaction.user != game.host:
                    await interaction.channel.send(f"{interaction.user.name} joined the game!")
                else:
                    await interaction.response.send_message("You are the host!", ephemeral=True)
            
            else:
                await interaction.response.send_message("You are already in the game.", ephemeral=True)


class GameGameplayView(View):
    def __init__(self, host_id, guild_id):
        super().__init__()
        self.host_id = host_id
        self.guild_id = guild_id

    @discord.ui.button(label="Leave Game", style=discord.ButtonStyle.danger, custom_id="leave_game")
    async def leave_game_button(self, interaction: discord.Interaction, button: Button):
        game = games.get(self.guild_id)
        
        if not game:
            await interaction.response.send_message("You can't leave from a game that is not ongoing.", ephemeral=True)
            return
        
        user = interaction.user
        
        # Proovi mängija eemaldada
        if game.remove_player(user):
            await interaction.response.send_message(f"{user.display_name} has left the game.")
        # Mängija ei olnud selles mängus
        else:
            await interaction.response.send_message(f"Couldn't leave from the game.", ephemeral=True)
            
        if game.host == user:
            # Määra uus host
            game.set_host(game.players[0])
            await interaction.response.send(f"Host left the game, the new host is {game.host.display_name}")
                
        # Liiga vähe mängijaid, et mängu jätkata
        if len(game.players) < 2:
            await interaction.channel.send("Not enough players to continue the game.\nGame has ended.")
            del games[self.guild_id]
            print("Game ended")
        
        
        
        # if game:
        #     player_id = interaction.user.id

        #     if player_id in map(lambda a: a.user_id, game.players):
        #         for player in game.players:
        #             if player.user_id == player_id:
        #                 game.players.remove(player)
        #                 break
                
        #         for player in game.player_order:
        #             if player.user_id == player_id:
        #                 game.player_order.remove(player)

        #         if player_id == game.host.id:
        #             if len(game.players) == 1:
        #                 await interaction.channel.send(
        #                     f"{interaction.user.name} left the game. Only one player remains. The game has ended.")
        #                 del games[self.guild_id]
        #                 return
        #             else:
        #                 new_host_id = game.player_order[0].user_id
        #                 game.host = interaction.guild.get_member(new_host_id)
        #                 await interaction.channel.send(f"{game.host.name} is now the new host of the game.")

        #         await interaction.response.send_message(f"{interaction.user.name} has left the game.", ephemeral=True)
        #     else:
        #         await interaction.response.send_message("You are not in the game.", ephemeral=True)

    @discord.ui.button(label="End Game", style=discord.ButtonStyle.green, custom_id="end_game")
    async def end_game_button(self, interaction: discord.Interaction, button: Button):
        game = games.get(self.guild_id)
        if not game:
            await interaction.response.send_message("No active game found in this channel.", ephemeral=True)
            return

        if game.host is None:
            # See ei tohiks mitte kunagi juhtuda
            await interaction.response.send_message("No host assigned for this game.", ephemeral=True)
            return

        if interaction.user != game.host:
            await interaction.response.send_message("Only the host can end the game!", ephemeral=True)
            return

        # Host lõpetab mägnu
        del games[self.guild_id]
        await interaction.response.send_message("The game has ended!", ephemeral=False)


    @discord.ui.button(label="View Cards", style=discord.ButtonStyle.blurple, custom_id="view_cards")
    async def view_cards_button(self, interaction: discord.Interaction, button: Button):
        game: GameManager = games.get(self.guild_id)
        
        if not game:
            return
        
        player = game.get_player_by_id(interaction.user.id)
        embed = game.get_player_embed(player)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
            
        
        
        # game = games.get(self.guild_id)
        # if game:
        #     player_id = interaction.user.id

        #     is_current_turn = (player_id == game.player_order[game.current_turn_index].user_id)

        #     cards_in_hand = 0
        #     for player in game.players:
        #         if player.user_id == player_id:
        #             cards_in_hand = len(player.cards)
            
        #     cards_message = f"You have {cards_in_hand} cards."
        #     if is_current_turn:
        #         cards_message += "\nIt's your turn"

        #     await interaction.response.send_message(cards_message, ephemeral=True)


    # @discord.ui.button(label="View Cards", style=discord.ButtonStyle.blurple, custom_id="view_cards")
    # async def view_cards_button(self, interaction: discord.Interaction, button: Button):
    #     game = games.get(self.guild_id)
    #     if game:
    #         player_id = interaction.user.id

    #         is_current_turn = (player_id == game.player_order[game.current_turn_index].user_id)

    #         cards_in_hand = 0
    #         for player in game.players:
    #             if player.user_id == player_id:
    #                 cards_in_hand = len(player.cards)
            

    #         cards_message = f"You have {cards_in_hand} cards."
    #         if is_current_turn:
    #             cards_message += "\nIt's your turn"

    #         await interaction.response.send_message(cards_message, ephemeral=True)


@bot.command()
async def uno(ctx):
    if ctx.guild.id in games:
        await ctx.send("A game is already ongoing in this server!")
        return
    discord.Member
    

    host = ctx.author
    games[ctx.guild.id] = GameManager()  # Loo uus mäng
    games[ctx.guild.id].set_host(host)  # Lisa host mägnijate hulka ning määra ta ka hostiks
    
    view = GameControlView(host.id, ctx.guild.id)
    await ctx.send(
        "Welcome to Uno! Click below to join the game and get started.",
        view=view
    )
    

@bot.command()
async def a(ctx):
    
    print(type(ctx.message.author.display_avatar))
    
    players_list = ["Ketsupi siil", "Player2", "Player3", "Player4"]
    
    embed_author = "Ketsupi siil's turn"
    # embed_title = "Player4 Played blue reverse"

    last_player_name = players_list[1]
    embed_desc = f"{last_player_name} played blue reverse\n"
    
    field_value = ""
    for index, name in enumerate(players_list):
        selected = False
        if index == 0:
            field_value += ":crown: "  # The host
            selected = True
        else:
            field_value += ":bust_in_silhouette: "
        field_value += f"{'**' if selected else ''}{name}{'**' if selected else ''}{'' if len(players_list) == index + 1 else '\n'}"
    # embed_desc = "**Players:**\n:crown:**Ketsupi siil**\n:bust_in_silhouette:Player2\n:bust_in_silhouette:Player3\n:bust_in_silhouette:Player4"
    

    embed_color = discord.Color.blue()
    
    image_file = discord.File("./images/BlueReverse.png", filename="bluuuuuu.png")
    embed = discord.Embed(description=embed_desc, color=embed_color)
    # embed = embed.set_image(url="attachment://bluuuuuu.png")  # big image at the bottom
    embed.set_thumbnail(url="attachment://bluuuuuu.png")  # small image at the right
    embed.set_author(name=embed_author, icon_url="https://cdn.discordapp.com/avatars/681940138020044820/10a15098118807ae3d1f88532fb990dc.webp?size=128")
    embed.add_field(name="**Players:**", value=field_value, inline=False)
    
    await ctx.send(file=image_file, embed=embed)

@bot.tree.command(name='hello')
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(content='yo', ephemeral=True)

@bot.command()
async def sync_tree(ctx: commands.Context) -> None:
    """Sync app commands to Discord."""
    print("syncing")
    await ctx.bot.tree.sync()
    await ctx.send('Application commands synchronized!')

token = None
with open("discord_token.txt", "r") as f:  # will raise an exception if file is not found
    token = f.readline().strip()  # Make it naked

if token:
    bot.run(token)
else:
    print("ERROR! No discord bot token was supplied")
