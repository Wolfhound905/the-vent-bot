import discord
from discord.ext import commands
from configuration import get_welcome_channel
import os
from PIL import Image, ImageDraw, ImageOps, ImageFont
from io import BytesIO

channelID = int(get_welcome_channel())

class welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def make_welcome_image(self, user: discord.Member):
        welcome = Image.open("/home/wolfhound/discord-bots/the-vent-bot/resources/welcome_template.png")

        asset = user.avatar_url_as(size = 256)

        data = BytesIO(await asset.read())
        pfp = Image.open(data)
        pfp = pfp.resize((310, 310))

        offset = (pfp.width - pfp.height) // 2
        pfp = pfp.crop((offset, 0, pfp.height + offset, pfp.height))

        mask = Image.new("L", pfp.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + pfp.size, fill=255)

        out = ImageOps.fit(pfp, mask.size, centering=(0.5, 0.5))
        out.putalpha(mask)

        welcome.paste(out, (28, 19))

        font = ImageFont.truetype("/home/wolfhound/discord-bots/the-vent-bot/resources/arial.ttf", 50)
        draw = ImageDraw.Draw(welcome)

        text = f"Welcome {user.name}"
        draw.text((946/2,400), text, (255,255,255), font=font, anchor="mm")
        text = f"Member #{user.guild.member_count}"
        draw.text((946/2,450), text, (255,255,255), font=font, anchor="mm")

        welcome.save("/home/wolfhound/discord-bots/the-vent-bot/resources/welcome_pfp.png")

    @commands.Cog.listener()
    async def on_member_join(self, member):

        await self.make_welcome_image(member)

        if member.guild.id == 759715539622428673:
            await self.bot.get_channel(channelID).send(content=f"""
            Hey {member.mention} Welcome to **{member.guild.name}**!
            """, file= discord.File("/home/wolfhound/discord-bots/the-vent-bot/resources/welcome_pfp.png"))
            os.remove("./resources/welcome_pfp.png")

    # @commands.command(name='test')
    # async def test(self, ctx):
    #     user: discord.Member = ctx.author

    #     await self.make_welcome_image(user)

    #     await ctx.send(content="here", file= discord.File("/home/wolfhound/discord-bots/the-vent-bot/resources/welcome_pfp.png"))
    #     os.remove("./resources/welcome_pfp.png")


def setup(bot):
    bot.add_cog(welcome(bot))
