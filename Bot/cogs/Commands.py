import nextcord

from Bot.core.Core import Core


class Commands(Core):
    def __init__(self, bot):
        super().__init__(bot=bot)
        self.bot = bot

    @nextcord.slash_command(name="ping", description="bot latency")
    async def ping(self, ctx):
        await ctx.send("Pong! {}ms".format(round(self.bot.latency, 2) * 1000))


def setup(bot):
    bot.add_cog(Commands(bot))
