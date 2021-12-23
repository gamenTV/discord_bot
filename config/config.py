from os.path import dirname
from json import load, dump


class ConfigTool:
    def __init__(self):
        config_path = dirname(__file__) + "\\config.json"
        self.config = load(open(config_path))

    async def change_config(self, ctx, cat, conf_name, value):
        self.config[cat][conf_name] = value
        dump(self.config, open(self.config_path, "w"))
        if conf_name == "free_games_channel":
            return self.reload_channel(ctx)

    async def reload_channel(self, client):
        return client.get_channel(self.config["free_games"]["free_games_channel"])

    async def get_config(self, cat, conf_name):
        return self.config[cat][conf_name]
