import os

import nextcord
import requests

from Bot.core import Core

ADMIN_IDS = [int(value) for value in os.getenv("ADMIN_IDS").split(",")]
GUILD_IDS: list[int] = [int(value) for value in os.getenv("GUILD_IDS").split(",")]


def get_ngrok_url():
    try:
        response = requests.get('http://localhost:4040/api/tunnels')
        data = response.json()
        if 'tunnels' in data:
            for tunnel in data['tunnels']:
                if tunnel['proto'] == 'https':
                    return tunnel['public_url']
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching ngrok URL: {e}")
        return None


def get_service_url():
    # 首先嘗試獲取 ngrok URL
    ngrok_url = get_ngrok_url()
    if ngrok_url:
        return ngrok_url
    else:
        # 如果 ngrok 不可用，則使用本地 URL
        return "http://localhost:5000"


HOST_URL = get_service_url()


class Commands(Core):
    def __init__(self, bot):
        super().__init__(bot=bot)
        self.bot = bot

    @nextcord.slash_command(description="help command", guild_ids=GUILD_IDS)
    async def help(self, ctx):
        if ctx.user.id == self.bot.user.id:
            return

        channel = self.bot.get_channel(ctx.channel_id)
        embed_message = nextcord.Embed(
            title="help",
            description="The introduction of the commands.",
            colour=nextcord.Color.green()
        ).add_field(
            name="</link:1251903708711882792>",
            value="Give the service link.",
            inline=False
        ).add_field(
            name="</ping:1246407256086413362>",
            value=f"Latency of the bot.",
            inline=False
        ).add_field(
            name="</choose_a_category:1251887853252776008>",
            value=f"The categories you choose and get the emotions.",
            inline=False
        )
        async with channel.typing():
            if ctx.user.id in ADMIN_IDS:
                admin_embed_message = nextcord.Embed(
                    title="Welcome admin",
                    description="This is admin's help command",
                    colour=nextcord.Color.blue()
                ).add_field(
                    name="</crawler ptt:1246407254861680700>",
                    value="To get every categories' emotions. This is very dangerous if you have no api token usages.",
                    inline=False
                ).add_field(
                    name="</reload:1235113013665726514>",
                    value="To reload the extension you have been changed.",
                    inline=False
                )

                await ctx.send(embeds=[admin_embed_message, embed_message])
            else:
                await ctx.send(embed=embed_message)

    @nextcord.slash_command(name="link", description="What is the link?", guild_ids=GUILD_IDS)
    async def link(self, ctx):
        if ctx.user.id == self.bot.user.id:
            return
        embed_message = nextcord.Embed(
            title="這是首頁連結",
            description=HOST_URL,
            colour=nextcord.Color.green()
        )
        await ctx.send(embed=embed_message)

    @nextcord.slash_command(name="ping", description="bot latency", guild_ids=GUILD_IDS)
    async def ping(self, ctx):
        if ctx.user.id == self.bot.user.id:
            return
        await ctx.send("Pong! {} ms".format(round(self.bot.latency, 2) * 1000))


def setup(bot):
    bot.add_cog(Commands(bot))
