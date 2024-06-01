import os
import nextcord

from Bot.core import Core

GUILD_IDS: list[int] = [int(value) for value in os.getenv("GUILD_IDS").split(",")]


class Crawler(Core):
    def __init__(self, bot):
        super().__init__(bot=bot)
        self.bot = bot

    @nextcord.slash_command(name="crawler", description="get ppt articles' emotion", guild_ids=GUILD_IDS)
    async def crawler(self, ctx):
        await ctx.send("Pong! {} ms".format(round(self.bot.latency, 2) * 1000))


def setup(bot):
    bot.add_cog(Crawler(bot))
