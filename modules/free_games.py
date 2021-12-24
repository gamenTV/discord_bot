from discord import Game, Embed, Colour
from os.path import dirname
from datetime import datetime
from json import load, dump


class FreeGames:
    def __init__(self, client, channel, role, colour):
        self.client = client
        self.json_path = dirname(__file__)+"\\free_games.json"
        self.json_data = load(open(self.json_path))
        self.embed_colour = colour
        self.channel = channel
        self.role = role

    async def func_check_games(self):
        delete = []
        await self.client.change_presence(activity=Game('Check Games!'))
        time = datetime.now().strftime("%d.%m.%Y %H:%M")
        for game in self.json_data:
            json_game = self.json_data[game]
            if json_game["expires"] < time:
                try:
                    msg_id = json_game["message_id"]
                    msg = await self.channel.fetch_message(msg_id)
                except Exception as e:
                    delete.append(game)
                    continue

                if json_game["expires"] < time:
                    if msg:
                        await msg.delete()
                        delete.append(game)
            elif (json_game["message_id"] is None) and (json_game["start"] < time):
                message = await self.send_game_msg(game, json_game["expires"],
                                                   json_game["link"], json_game["price"], json_game["id"], json_game["color"])
                json_game["message_id"] = message.id

        for game in delete:
            del self.json_data[game]
        else:
            dump(self.json_data, open(self.json_path, "w"))

        await self.client.change_presence(activity=Game('Idling!'))

    async def func_create_game(self, titel, start, expires, link, price, id, color):
        if datetime.strptime(expires, "%d.%m.%Y %H:%M"):
            self.json_data[titel] = {"start": start, "expires": expires, "link": link, "price": price, "message_id": None, "id": id, "color": color}
            dump(self.json_data, open(self.json_path, "w"))

    async def send_game_msg(self, titel, expires, link, price, id, color):
        embed = Embed(title=titel, description='Expires **'+expires+"** Uhr", color=int(color, 16)) #ToDo: int(self.embed_colour, 16))
        embed.add_field(name="**Link**", value=f"**||{link}||**", inline=False)
        embed.add_field(name="**Price**", value=f"**~~{price}~~€**", inline=False)
        embed.set_footer(text="Free Games everytime i post :) ID "+id, icon_url="https://i.imgur.com/uZIlRnK.png")

        message = await self.channel.send(f"<@&{self.role}>", embed=embed)

        return message

    async def send_private_msg(self, user_id, game_id):
        user = await self.client.fetch_user(user_id)
        for game in self.json_data:
            json_game = self.json_data[game]
            if json_game["id"] == game_id:
                    embed = Embed(title=game, description='Expires **' + json_game["expires"] + "** Uhr",
                                  color=int(json_game["color"], 16))  # ToDo: int(self.embed_colour, 16))
                    embed.add_field(name="**Link**", value=json_game["link"], inline=False)
                    embed.add_field(name="**Price**", value=f"**~~"+json_game["price"]+"~~€**", inline=False)
                    embed.set_footer(text="Free Games everytime i post :) ID " + game_id,
                                     icon_url="https://i.imgur.com/uZIlRnK.png")

                    message = await user.send(embed=embed)

                    return message
        else:
            dump(self.json_data, open(self.json_path, "w"))