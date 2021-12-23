from discord import Game
from discord.ext import commands, tasks
from modules.free_games import FreeGames
from config.config import ConfigTool

token = ""

client = commands.Bot(command_prefix='.')
ConfigFunc = ConfigTool()

#test

@client.event
async def on_ready():
    await client.change_presence(activity=Game(""))
    global FreeGamesFunc
    FreeGamesFunc = FreeGames(client, await ConfigFunc.reload_channel(client),
                              await ConfigFunc.get_config("free_games", "free_games_role"),
                              await ConfigFunc.get_config("free_games", "embed_color"))
    check_for_expired.start()


@client.command()
async def setting(ctx, cat, conf_name, value):
    reload = ConfigFunc.change_config(ctx, cat, conf_name, value)
    if conf_name == "free_games_channel":
        global FreeGamesFunc
        FreeGamesFunc(client, reload) #ToDo: Suche nach möglichkeit Configuration neu zu laden
                                      # !!!ohne einzelnd zu Definieren!!!


@client.command()
async def new_game(ctx, titel, start, expires, link, price):
    await FreeGamesFunc.func_create_game(titel, start, expires, link, price)
    await ctx.message.delete()


@tasks.loop(minutes=5.0)
async def check_for_expired():
    await FreeGamesFunc.func_check_games()
    
client.run(token)
