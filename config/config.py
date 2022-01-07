from os.path import dirname
from json import load, dump
from discord_components import Select, SelectOption, Button, ButtonStyle
from discord.utils import get
from discord import Embed

config_path = dirname(__file__) + "\\config.json"
config = load(open(config_path))


async def get_config():
    return config


async def save_config():
    dump(config, open(config_path, "w"), indent=4)


async def select_color(ctx, client):
    colors = config['embed_colors']['value']
    text = await ctx.send("Choose a Color:")
    spam = [text]
    for color in colors:
        embed = Embed(title=colors[color]['label'],
                      color=int(colors[color]['value'].replace("#", ""), 16),
                      description=f"Hex color Code: {colors[color]['value']}")
        color_but = Button(style=ButtonStyle.grey, label="Select", id=color)
        msg = await ctx.send(embed=embed, components=[color_but])
        spam.append(msg)
    but_click = await client.wait_for("button_click")
    for s in spam:
        await s.delete()
    id = but_click.component.id
    return colors[id], id


async def change_setting(ctx, client):
    manager_role = config["manager"]["value"]
    roles = ctx.message.author.roles
    manager = [role for role in roles if int(role.id) == manager_role]
    if ctx.message.author.guild_permissions.administrator or manager:
        editor = ctx.message.author

        def generate_options(values):
            drop_options = []
            for val in values:
                drop_options.append(SelectOption(label=values[val]['label'], value=val,
                                                 description=values[val]['description']))
            return drop_options

        async def get_new_value(label, value, val_type):
            msg = await ctx.send(content=f"Reply with a new Value for {label}. Current Value is: {str(value)}")
            reply = await client.wait_for("message", check=lambda i: i.author == editor)
            value = reply.content
            await reply.delete()
            await msg.delete()
            try:
                if val_type == "role":
                    return_value = int(value)
                    if not get(ctx.guild.roles, id=return_value):
                        await ctx.send("That's not a Valid Role ID!")
                        return
                elif val_type == "channel":
                    return_value = int(value)
                    if not get(ctx.guild.text_channels, id=return_value):
                        await ctx.send("That's not a Valid Channel ID!")
                        return
                elif val_type == "color":
                    return_value = value
                else:
                    await ctx.send("Error please Contact staff member!")
            except ValueError:
                await ctx.send("Something went wrong Contact a Staff member!")
                return
            return return_value

        drop = await ctx.send(content="Select the Category",
                              components=[Select(placeholder="Categories", options=generate_options(config))])
        await ctx.message.delete()
        event = await client.wait_for('select_option', check=None)
        cat = event.values[0]
        options = config[cat]['value']
        await drop.delete()

        if cat == "free_games":
            drop = await ctx.send(content="Select the Option",
                                  components=[Select(placeholder="Categories", options=generate_options(options))])

            event = await client.wait_for('select_option', check=None)
            option_name = event.values[0]
            option = config[cat]['value'][option_name]
            label = option['label']
            await drop.delete()
            new_value = await get_new_value(option["label"], option["value"], option["type"])
            if new_value:
                config[cat]['value'][option_name]['value'] = new_value
        elif cat == "manager":
            option = config[cat]
            label = option['label']
            new_value = await get_new_value(option["label"], option["value"], option["type"])
            if new_value:
                config[cat]['value'] = new_value
        elif cat == "embed_colors":
            embed = Embed(title="Choose your Color Option:")
            new_color = Button(style=ButtonStyle.grey, label="New Color", id="new_color")
            change_color = Button(style=ButtonStyle.grey, label="Edit Color", id="change_color")
            delete_color = Button(style=ButtonStyle.grey, label="Delete Color", id="delete_color")
            buttons = await ctx.send(embed=embed, components=[[new_color, change_color, delete_color]])

            but_click = await client.wait_for("button_click")
            await buttons.delete()
            if but_click.component.id == "new_color":
                ctx.send("")
                return
            elif but_click.component.id == "change_color":
                await ctx.send("Which color do you want to edit?:")
                color, id = await select_color(ctx)
                label = color["label"]
                while True:
                    new_value = await get_new_value(color["label"], color["value"], "color")
                    config[cat]['value'][id]['value'] = new_value
                    embed = Embed(title="Is that the right Color?",
                                  color=int(new_value.replace("#", ""), 16))
                    yes = Button(style=ButtonStyle.grey, label="Yes", id="yes")
                    no = Button(style=ButtonStyle.grey, label="No", id="no")
                    msg = await ctx.send(embed=embed, components=[[yes, no]])
                    check = await client.wait_for("button_click")
                    await msg.delete()
                    if check.component.id == "yes":
                        break

            elif but_click.component.id == "delete_color":
                if len(config['embed_colors']['value']) > 1:
                    msg = await ctx.send("Which color do you want to delete?")
                    color, id = await select_color(ctx)
                    await msg.delete()
                    del config[cat]['value'][id]
                else:
                    await ctx.send("You cant delete the last Color!")
                    return
                await ctx.send(f"{color} got Deleted!")
                await save_config()
                return

        await save_config()
        respond = f"""The new Value for {label} is {new_value}. Changes will be applied at the next restart!"""
        await ctx.send(respond)
    else:
        await ctx.send("You do not have Permissions to do that!")
