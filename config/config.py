from os.path import dirname
from json import load, dump
from discord_components import Select, SelectOption


class ConfigTool:
    def __init__(self, client):
        config_path = dirname(__file__) + "\\config.json"
        self.config = load(open(config_path))
        self.client = client

    async def reload_channel(self):
        return self.client.get_channel(self.config["free_games"]["free_games_channel"]["value"])

    async def get_config(self, cat):
        return self.config[cat]

    async def change_setting(self, ctx):
        await ctx.message.delete()
        await ctx.send(content="Select the Category", components=
        [Select(placeholder="Categories", options=[
            SelectOption(
                label="Free Games Options",
                value="free_games",
                description="Everything about the Free Games"
            )
        ])])

        event = await self.client.wait_for('select_option', check=None)
        await event.send(event.values[0])
        cat = event.values[0]

        options = await self.get_config(cat)
        drop_options = []

        for option in options:
            drop_options.append(SelectOption(label=options[option]["label"],
                                             value=option,
                                             description=options[option]["description"]))

        await ctx.send(content="Select the Category",
                       components=[Select(placeholder="Categories", options=drop_options)])

        event = await self.client.wait_for('select_option', check=None)
        option = event.values[0]

        await ctx.send(
            f"Reply with a new Value for {options[option]['label']}. Current Value is: {options[option]['value']}")
        msg = await self.client.wait_for("reply", check=None)
        await ctx.send("Bam!")


if __name__ == "__main__":
    ConfigTool = ConfigTool()
    conf = ConfigTool.get_config("free_games", "free_games_role")
    print(conf)
