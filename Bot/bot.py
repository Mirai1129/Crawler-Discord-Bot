import os
import dotenv
import nextcord
from nextcord.ext import commands

dotenv.load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

if os.getenv("DEPLOYMENT_ENV") == "prod":
    dotenv.load_dotenv("../config/.env.prod")
if os.getenv("DEPLOYMENT_ENV") == "beta":
    dotenv.load_dotenv("../config/.env.beta")

GUILD_IDS: list[int] = [int(value) for value in os.getenv("GUILD_IDS").split(",")]
ADMIN_IDS: list[int] = [int(value) for value in os.getenv("ADMIN_IDS").split(",")]

bot = commands.Bot()

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')


@bot.event
async def on_ready():
    activity = nextcord.ActivityType.streaming
    print(f'We have logged in as {bot.user}')
    await bot.change_presence(status=nextcord.Status.dnd,
                              activity=nextcord.Activity(type=activity, name="cool"))


@bot.slash_command()
async def reload(ctx, extension: str):
    if ctx.user.id in ADMIN_IDS:
        bot.reload_extension(f'cogs.{extension}')
        await ctx.send(f'Reloaded: {extension}', ephemeral=True)
    else:
        await ctx.send('You are not an administrator!', ephemeral=True)


if __name__ == '__main__':
    bot.run(TOKEN)
