from discord.ext import commands
from discord.ui import View, Button
import discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class GameManager:
    def __init__(self, host):
        self.host = host
        self.players = {}
        self.player_order = []  # Mängijate järjekord
        self.current_turn_index = 0  # Alguses on esimene mängija host

    def start_game(self):
        self.current_turn_index = 0  # Määrame, et mäng algab hostiga

    def add_player(self, user):
        if user.id in self.players:
            return False
        self.players[user.id] = user.name
        self.player_order.append(user.id)
        return True

games = {}
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

        await interaction.response.send_message(f"It's {game.host.name}'s turn!")

        player_info = f"{game.host.name}'s turn\n"
        for index, player_id in enumerate(game.player_order):
            if index == 0:
                continue  #
            player_name = game.players[player_id]
            player_info += f"{player_name}: 0 cards\n"  #
        game_view = GameGameplayView(game.host.id, self.guild_id)

        await interaction.followup.send(player_info, view=game_view)
    @discord.ui.button(label="Join Game", style=discord.ButtonStyle.green, custom_id="join_game")
    async def join_game_button(self, interaction: discord.Interaction, button: Button):
        game = games.get(self.guild_id)
        if game:
            player_id = interaction.user.id
            if player_id not in game.players:
                game.players[player_id] = interaction.user
                game.player_order.append(player_id)

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
        if game:
            player_id = interaction.user.id

            if player_id in game.players:
                del game.players[player_id]
                game.player_order.remove(player_id)

                if player_id == game.host.id:
                    if len(game.players) == 1:
                        await interaction.channel.send(
                            f"{interaction.user.name} left the game. Only one player remains. The game has ended.")
                        del games[self.guild_id]
                        return
                    else:
                        new_host_id = game.player_order[0]
                        game.host = interaction.guild.get_member(new_host_id)
                        await interaction.channel.send(f"{game.host.name} is now the new host of the game.")

                await interaction.response.send_message(f"{interaction.user.name} has left the game.", ephemeral=True)
            else:
                await interaction.response.send_message("You are not in the game.", ephemeral=True)

    @discord.ui.button(label="End Game", style=discord.ButtonStyle.green, custom_id="end_game")
    async def end_game_button(self, interaction: discord.Interaction, button: Button):
        game = games.get(self.guild_id)
        if not game:
            await interaction.response.send_message("No active game found in this channel.", ephemeral=True)
            return

        if game.host is None:
            await interaction.response.send_message("No host assigned for this game.", ephemeral=True)
            return

        if interaction.user.id != game.host.id:
            await interaction.response.send_message("Only the host can end the game!", ephemeral=True)
            return

        del games[self.guild_id]
        await interaction.response.send_message("The game has ended!", ephemeral=False)


    @discord.ui.button(label="View Cards", style=discord.ButtonStyle.blurple, custom_id="view_cards")
    async def view_cards_button(self, interaction: discord.Interaction, button: Button):
        game = games.get(self.guild_id)
        if game:
            player_id = interaction.user.id

            is_current_turn = (player_id == game.player_order[game.current_turn_index])

            cards_message = f"You have {0} cards."
            if is_current_turn:
                cards_message += "\nIt's your turn"

            await interaction.response.send_message(cards_message, ephemeral=True)


    @discord.ui.button(label="View Cards", style=discord.ButtonStyle.blurple, custom_id="view_cards")
    async def view_cards_button(self, interaction: discord.Interaction, button: Button):
        game = games.get(self.guild_id)
        if game:
            player_id = interaction.user.id

            is_current_turn = (player_id == game.player_order[game.current_turn_index])

            cards_message = f"You have {0} cards."
            if is_current_turn:
                cards_message += "\nIt's your turn"

            await interaction.response.send_message(cards_message, ephemeral=True)


@bot.command()
async def uno(ctx):
    if ctx.guild.id in games:
        await ctx.send("A game is already ongoing in this server!")
        return

    host = ctx.author
    games[ctx.guild.id] = GameManager(host)

    view = GameControlView(host.id, ctx.guild.id)
    await ctx.send(
        "Welcome to Uno! Click below to join the game and get started.",
        view=view
    )


bot.run("MTMxMDkwODg3ODg2MjQyMjEyNw.G2w9Ce.TkHidTYKFPXuiOO56JpOEmBk9GeVMXeSCeeqCQ")
