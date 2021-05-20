import re
from os import path, remove
import discord
import requests
from bs4 import BeautifulSoup
from colored_print import ColoredPrint
from discord.ext import commands

log = ColoredPrint()

mimes = ["video", "image", "text/"]  # Note, checks five characters!

blacklist_path = "/home/wolfhound/discord-bots/the-vents-bot/resources/blacklist.txt"

class crashPrevention(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    def Find(self, string):
        regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        url = re.findall(regex, string)
        return [x[0] for x in url]



    def checkMIME(self, mimeType):
        for x in mimes:
            if mimeType[0:5].lower() == x[0:5]:
                return mimeType  # Whatever mimeType is, it will be truthy
        return False

    def checkContent(self, url):  # Uses Return HTTP headers to detect filetype
        r = requests.get(url, stream=True)
        contentType = r.headers["Content-Type"].split(";")[0]
        return self.checkMIME(contentType)




    def checkFile(self, url):
        url = url.replace("\\", "")  # No need for backslash in the urls
        if "thumbs.gfycat.com" in url:  # Gfycat is the source for most of these
            # Both crash, only second is detectable
            url = url.replace("-max-1mb.gif", "-mobile.mp4")
            url = url.replace(".webp", "-mobile.mp4")
            url = url.replace("-size_restricted.gif", "-mobile.mp4")  # see above
        if "media.giphy.com" in url: # mp4 are easier to read and less compressed.
            url = url.replace("media.", "i.")
            url = url.replace(".gif", ".mp4")
        # TODO Check Blacklist
        r = requests.get(url, allow_redirects=True)
        urlName = url[8:]
        urlName = f'{urlName}'.replace('/', '')  # Uses URL to name files
        open(urlName, "wb").write(r.content)
        with open(urlName, "rb") as f:
            s = f.read()
        exploitTypes = [
            # This is an abnormal part of some crash mp4's. Most, if not all mp4's need stts, but not (stts
            b"(stts",
        ]

        for exploits in exploitTypes:
            test = s.find(exploits)
            if test != -1:
                remove(urlName)
                log.err(f"Found {exploits}. Character {test}\nThis was a client crasher\n")
                return True
        options_1 = s.find(b'options')
        if options_1 != -1:
            options_2 = s.find(b'options', options_1 + 1)
            if options_2 != -1:
                log.err("Found multiple options in same file.") # discord doesnt like this
                remove(urlName)
                return True
        remove(urlName)  # Delete the file
        return False


    def checkLink(self, url):  # Mostly applies to (gfycat and giphy), but uses og:video to find what discord embeds
        url = url.replace("\\", "")
        r = requests.get(url, allow_redirects=True)
        soup = BeautifulSoup(str(r.content), "html.parser")
        mp4 = soup.find("meta", property="og:video")
        log.success(
            f'Has og:video, now using: {mp4["content"]}\n' if mp4 else "No meta mp4 given\n")
        if mp4:
            return self.checkFile(mp4["content"])  # If there is an og:video
        else:
            return False


    def updateBlacklist(self, url):  # Adds url to blacklist.txt if not already added
        if self.checkBlacklist(url):
            return
        else:
            with open(blacklist_path, "a") as f:
                f.write(f'{url}\n')


    def checkBlacklist(self, url):  # Reads blacklist.txt to check if url appears
        with open(blacklist_path) as blacklist:
            for x in blacklist:
                if f"{url}\n" == x:
                    return True
        return False


    async def checkMessage(self, message):
        crashMessage = f"Fun Fact: {message.author.mention} does know crashing gifs are dumb. ||Like them||"
        urls = self.Find(message.content)  # Get URLs
        if message.attachments:  # If the message has attachments
            for Attachment in message.attachments:
                url = Attachment.url
            log.info(url)
            crasher = self.checkFile(url)
            if crasher:
                await message.delete()
                await message.channel.send(crashMessage, allowed_mentions=discord.AllowedMentions.none())
                return
            else:
                log.success("This probably doesnt contain a crash\n")
        if urls:  # If the message contains a url
            for url in urls:
                if self.checkBlacklist(url):
                    await message.delete()
                    await message.channel.send(crashMessage, allowed_mentions=discord.AllowedMentions.none())
                    return
                log.warn(f"Getting {url}")
                # If the site uses head meta tags for the file link
                if self.checkContent(url) == "text/html":
                    log.info("The link was text/html")
                    crasher = self.checkLink(url)
                else:
                    log.info("The link was video/gif")
                    crasher = self.checkFile(url)
                if crasher:
                    await message.delete()
                    self.updateBlacklist(url)
                    await message.channel.send(crashMessage, allowed_mentions=discord.AllowedMentions.none())
                    return
                else:
                    log.success("This probably doesnt contain a crash\n")


    @commands.Cog.listener()
    async def on_message(self, message):
        await self.checkMessage(message)

def setup(bot):
    bot.add_cog(crashPrevention(bot))




