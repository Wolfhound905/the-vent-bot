import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from configuration import get_guilds

guilds = get_guilds()

class helpMenu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
     
    @cog_ext.cog_slash(name="help", description='Use this command to view what you can do', guild_ids = guilds)
    async def group_say(self, ctx: SlashContext):
        embed=discord.Embed(title="Help Menu", description=f'A list of all slash commands to use with "{self.bot.user.name}"', color=0xf6c518)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(name="Whoah", value="Still working on this, will be updated soon™", inline=False)
        embed.set_footer(text="Keep on venting!", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)   
             
def setup(bot):
    bot.add_cog(helpMenu(bot))
