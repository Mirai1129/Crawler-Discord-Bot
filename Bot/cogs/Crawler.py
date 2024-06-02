import os

import nextcord
import requests
from nextcord.ext import commands

from Bot.core import Core
from Features import PttCrawler

FLASK_URL = "http://127.0.0.1:5000"
GUILD_IDS: list[int] = [int(value) for value in os.getenv("GUILD_IDS").split(",")]


class Crawler(Core):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(bot=bot)
        self.bot = bot
        self.crawler = PttCrawler()

    @nextcord.slash_command(name="crawler", description="Crawler commands", guild_ids=GUILD_IDS)
    async def crawler(self, ctx):
        pass

    @crawler.subcommand(name="ptt", description="get ppt articles' emotion")
    async def ptt(self, ctx):
        channel = self.bot.get_channel(ctx.channel_id)
        author = self.bot.get_user(ctx.author_id)

        if author == self.bot.user:
            return

        response = requests.post(f"{FLASK_URL}/emotions")
        async with channel.typing():
            await ctx.send("正在爬取文章...")


def setup(bot):
    bot.add_cog(Crawler(bot))
