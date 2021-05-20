import discord
from discord.ext import commands


class applications(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
     
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.webhook_id is not None and message.channel.id == 764812451337994240:
            await message.add_reaction("👍")
            await message.add_reaction("👎")

             
def setup(bot):
    bot.add_cog(applications(bot))
