from discord import Game
from discord.ext import commands, tasks
from modules.free_games import FreeGames
from config.config import ConfigTool
from json import load
from os.path import dirname
from discord_components import ComponentsBot

token = load(open(dirname(__file__) + "\\config\\token.json"))["token"]

client = ComponentsBot(command_prefix='.')
ConfigFunc = ConfigTool(client)


@client.event
async def on_ready():
    await client.change_presence(activity=Game(""))
    free_config = await ConfigFunc.get_config("free_games")
    free_config_val = free_config["value"]

    global FreeGamesFunc
    FreeGamesFunc = FreeGames(client, await ConfigFunc.reload_channel(),
                              free_config_val["free_games_role"]["value"],
                              free_config_val["free_games_poster_role"]["value"],
                              free_config_val["embed_color"]["value"])
    check_for_expired.start()


@client.command()
async def setting(ctx):
    await ConfigFunc.change_setting(ctx)


@client.command()
async def new_game(ctx, titel, start, expires, link, price):
    color, id = await ConfigFunc.select_color(ctx)
    color = int(color['value'].replace("#", ""), 16)
    await FreeGamesFunc.func_create_game(ctx, titel, start, expires, link, price, color)
    await ctx.message.delete()


@tasks.loop(minutes=5.0)
async def check_for_expired():
    await FreeGamesFunc.func_check_games()

client.run(token)
