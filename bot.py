# bot.py
import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from configuration import get_token, get_guilds

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="_", intents=intents)
slash = SlashCommand(bot, sync_commands=False, override_type = True)
activity = discord.Activity(name='in the vents', type=discord.ActivityType.playing)


bot.load_extension("behaviors.help")
bot.load_extension("behaviors.welcome")
bot.load_extension("behaviors.adminCommands")


@bot.event
async def on_ready():
    print("ready")
    commands = slash.commands
    await bot.change_presence(activity=activity)
    print(" Commands ".center(14, "~"))
    for key in commands:
        print(commands[key].name)
    print("⸻⸻⸻⸻")     


  
bot.run(get_token())
