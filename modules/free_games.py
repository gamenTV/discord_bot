from discord import Game, Embed
from os.path import dirname
from requests import get
from datetime import datetime
from json import load, dump
from config.config import get_config, select_color

json_path = dirname(__file__) + "\\free_games.json"
json_data = load(open(json_path))


def free_config(config, value):
    return config["free_games"]["value"][value]["value"]


async def func_check_games(client):
    channel = client.get_channel(free_config(await get_config(), "free_games_channel"))
    delete = []
    await client.change_presence(activity=Game('Check Games!'))
    time = datetime.now().strftime("%d.%m.%Y %H:%M")
    for game in json_data:
        json_game = json_data[game]
        if json_game['expires'] < time:
            try:
                msg_id = json_game['message_id']
                msg = await channel.fetch_message(msg_id)
            except Exception as e:
                print(e)
                delete.append(game)
                continue

            if json_game["expires"] < time:
                if msg:
                    await msg.delete()
                    delete.append(game)
        elif (json_game['message_id'] is None) and (json_game['start'] < time):
            message = await send_game_msg(client, game, json_game['expires'], json_game['link'],
                                          json_game['price'], json_game['color'])
            json_game['message_id'] = message.id

    for game in delete:
        del json_data[game]
    else:
        dump(json_data, open(json_path, "w"), indent=4)

    await client.change_presence(activity=Game("Idling!"))


async def func_create_game(ctx, client):
    creator_role = free_config(await get_config(), "free_games_poster_role")
    channel = client.get_channel(free_config(await get_config(), "free_games_channel"))

    data = {
        "start": {
            "question": "Since when is the Game Free? (Example: 01.01.2022 17:00)",
            "type": "datetime",
            "value": None
        },
        "expires": {
            "question": "When dos the Game Expires? (Example: 01.01.2022 17:00)",
            "type": "datetime",
            "value": None
        },
        "name": {
            "question": "Enter the game name:",
            "type": str,
            "value": None
        },
        "price": {
            "question": "Please enter the Game Price without Currency symbol",
            "type": float,
            "value": None
        }
    }

    ask = await channel.send("Please reply with the FreeGame Link:")
    answer = await client.wait_for("message", check=lambda m: m.author == ctx.author)
    await ask.delete()
    link = answer.content
    await answer.delete()
    answer = link.split("/")
    if answer[2] == "store.steampowered.com":
        appID = answer[4]
        response = get(f"https://store.steampowered.com/api/appdetails/?appids={appID}&cc=de%22")
        j = response.json()
        game_data = j["{}".format(appID)]["data"]
        data["name"]["value"] = game_data["name"]
        data["price"]["value"] = game_data["price_overview"]["initial_formatted"][:-1]

    print(type(data["price"]["value"]))

    for d in data:
        if data[d]["value"] is None:
            while True:
                ask = await ctx.send(data[d]["question"])
                answer = await client.wait_for("message", check=lambda m: m.author == ctx.author)
                await answer.delete()
                await ask.delete()
                if data[d]["type"] == "datetime":
                    try:
                        datetime.strptime(answer.content, "%d.%m.%Y %H:%M")
                        data[d]["value"] = answer.content
                        break
                    except ValueError:
                        data[d]["question"] = "Wrong Formatting! \n" + data[d]["question"]

    color, id = await select_color(ctx, client)
    color = int(color['value'].replace("#", ""), 16)

    roles = ctx.message.author.roles
    if [role for role in roles if int(role.id) == creator_role]:
        json_data[data["name"]["value"]] = {"start": data["start"]["value"], "expires": data["expires"]["value"],
                                            "link": link, "price": data["price"]["value"],
                                            "message_id": None, "color": color}
        dump(json_data, open(json_path, "w"), indent=4)
    else:
        channel.send("You do not have Permission to do that!")


async def send_game_msg(client, titel, expires, link, price, color):
    channel = client.get_channel(free_config(await get_config(), "free_games_channel"))
    ping_role = free_config(await get_config(), "free_games_role")
    embed = Embed(title=titel, description=f"Expires **{expires}** Uhr",
                  color=color)
    embed.add_field(name="**Link**", value=f"**||{link}||**", inline=False)
    embed.add_field(name="**Price**", value=f"**~~{price}~~€**", inline=False)
    embed.set_footer(text="Free Games every time i post :)", icon_url="https://i.imgur.com/uZIlRnK.png")

    message = await channel.send(f"<@&{ping_role}>", embed=embed)

    return message
