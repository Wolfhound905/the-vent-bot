# This cog creates voice channels for users
# this may be executed with /room channel_name:name member_cap:optional

import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from configuration import get_guilds
from profanity_filter import ProfanityFilter
from database.voiceVCs import get_voice_channels, add_vc, remove_vc, get_command_message
import asyncio

guilds = get_guilds()


class createVC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    options = [
        {
            "name": "channel_name",
            "description": "Name of the voice channel you want to make.",
            "type": 3,
            "required": True
        },
        {
            "name": "member_cap",
            "description": "Optional variable for the number of people allowed in the call.",
            "type": 4,
            "required": False
        }
    ]


    @cog_ext.cog_slash(name="room", options=options, description="Create a temperary vc to chat and slam in!", guild_ids=guilds)
    async def room(self, ctx: SlashContext, channel_name: str, member_cap=0):
        voice_state = ctx.author.voice
        if voice_state is None:
            await ctx.send(hidden=True, content="You need to be in a voice channel to use this command.")
        else:
            pf = ProfanityFilter(languages=['en'])
            if pf.is_clean(channel_name):
                guild = ctx.guild
                category = ctx.author.voice.channel.category
                if member_cap >= 100 or member_cap <= -1:
                    await ctx.send(hidden=True, content=f"`{member_cap}` is out of range.\n1-99 is the vailid range for voice channel member caps.")
                    return
                channel_name = (channel_name[:97] + '...') if len(channel_name) > 97 else channel_name
                channel = await guild.create_voice_channel(channel_name, user_limit=member_cap, category=category, position=0)
                response = await ctx.send(f"I created the voice channel {channel.mention}!")
                logs_channel = self.bot.get_channel(835013284129669140)
                await logs_channel.send(content=f"{ctx.author.mention} ({ctx.author.id}) created the voice channel {channel_name}.", allowed_mentions=discord.AllowedMentions.none())
                add_vc(channel.id, response.channel.id, response.id)
                await ctx.author.move_to(channel=channel)
            else:
                logs_channel = self.bot.get_channel(835013284129669140)
                await ctx.send(content="You can not create a voice channel with profanity, this has been reported.")
                await logs_channel.send(content=f"""⸻⸻\n||<@&799294477880918038><@&828499567812411412><@&764412431459549196>||\n"
                                        {ctx.author.name} tried creating a profane voice channel ({channel_name})\n
                                        `?warn {ctx.author.id} Attempting to create a profane voice channel '{channel_name}'`""", allowed_mentions=discord.AllowedMentions.none())


    def get_message(self, message_id):
        message = get_command_message(message_id)
        message_id: int = message['id']
        channel_id: int = message['channel']
        channel = self.bot.get_channel(channel_id)
        message = channel.get_partial_message(message_id)
        return message


    async def channel_cooldown(self, channel_id):
        message = self.get_message(channel_id)
        x = 10
        while x > 0:
            await message.edit(content=f"Time left: {x} seconds")
            x = x -2
            await asyncio.sleep(2)


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if len(get_voice_channels()) > 0:
            if before.channel is not None:
                if before.channel.id in get_voice_channels():
                    if len(before.channel.members) == 0:
                        await self.channel_cooldown(before.channel.id)
                        if len(before.channel.members) == 0:
                            message = self.get_message(before.channel.id)
                            remove_vc(before.channel.id)
                            await before.channel.delete()
                            await message.edit(content=f"Everybody left `{before.channel.name}` so I deleted it.")
                        else:
                            message = self.get_message(before.channel.id)
                            await message.edit(content=f"I saved `{before.channel.name}` because you came back.")




def setup(bot):
    bot.add_cog(createVC(bot))
