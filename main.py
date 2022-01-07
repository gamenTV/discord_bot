from discord import Game
from discord.ext import tasks
from config.config import change_setting
from modules.free_games import func_create_game, func_check_games
from json import load
from os.path import dirname
from discord_components import ComponentsBot

token = load(open(dirname(__file__) + "\\config\\token.json"))["token"]
client = ComponentsBot(command_prefix='.')


@client.event
async def on_ready():
    await client.change_presence(activity=Game(""))
    check_for_expired.start()


@client.command()
async def setting(ctx):
    await change_setting(ctx, client)


@client.command()
async def new_game(ctx):
    await func_create_game(ctx, client)
    await ctx.message.delete()


@tasks.loop(minutes=5.0)
async def check_for_expired():
    await func_check_games(client)

client.run(token)
