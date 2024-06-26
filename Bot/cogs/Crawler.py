import base64
import logging
import os
import time
from typing import Any

import nextcord
import requests
from nextcord import SlashOption
from nextcord.ext import commands

from Bot.core import Core
from Features import PttCrawler
from Features.Api import OpenAIEmotionalAnalyzer
from Mongo import MongoAdapter

ADMIN_IDS: list[int] = [int(value) for value in os.getenv("ADMIN_IDS").split(",")]
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
        return "http://localhost:5000/"


HOST_URL = get_service_url()


def board_categories() -> dict[Any, Any] | None:
    crawler = PttCrawler()
    category_datas = crawler.get_board_categories()
    ignore_categories = ['HatePolitics', 'SuckMovies', 'Sucknovels', 'SuckcomicBM', 'Suckcomic', 'HatePicket',
                         'HateP_Picket', 'esahc', 'L_SecretGard']
    categories = {}
    if category_datas:
        for data in category_datas:
            # 假設 data 是 tuple (int, str, str)
            _, title, name = data
            if name not in ignore_categories:
                categories[title] = name
    return categories if categories else None


class Crawler(Core):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(bot=bot)
        self.bot = bot
        self.crawler = PttCrawler()
        self.db = MongoAdapter()
        self.ai = OpenAIEmotionalAnalyzer()

    @staticmethod
    def __encode_base64(message_id: int) -> str:
        message_id_bytes = message_id.to_bytes((message_id.bit_length() + 7) // 8, 'big')
        return base64.urlsafe_b64encode(message_id_bytes).rstrip(b'=').decode('ascii')

    @nextcord.slash_command(name="crawler", description="Crawler commands", guild_ids=GUILD_IDS)
    async def crawler(self, ctx):
        pass

    @crawler.subcommand(name="ptt", description="get ppt articles' emotion")
    async def ptt(self, ctx):
        # TODO 新增機器人回應連結
        if ctx.user.id == self.bot.user.id or ctx.user.id not in ADMIN_IDS:
            await ctx.send("你不是管理員", ephemeral=True)
            return
        channel = self.bot.get_channel(ctx.channel_id)
        async with channel.typing():
            embed_message = nextcord.Embed(
                title="已收到管理員爬取需求",
                description="爬取文章中",
                colour=nextcord.Color.blue()
            )
            message = await ctx.send(embeds=[embed_message])
            categories = board_categories()
            total_categories = len(categories)
            current_category = 0
            if not categories:
                embed_message = nextcord.Embed(
                    title="錯誤",
                    description="找不到可用的版面分類",
                    colour=nextcord.Color.red()
                )
                await message.edit(embed=embed_message)
                return

            for title, name in categories.items():
                current_category += 1
                embed_message = nextcord.Embed(
                    title="正在爬取文章",
                    description=f"正在爬取 {title} (共 5 頁) ...",
                    colour=nextcord.Color.red()
                )
                await message.edit(embed=embed_message)
                articles_data = self.crawler.get_article_data(name, 1)

                for article_data in articles_data:
                    embed_message = nextcord.Embed(
                        title="正在判斷情緒",
                        description=f"正在判斷 **{article_data['title']}** 的情緒 ...",
                        colour=nextcord.Color.red()
                    )
                    await message.edit(embed=embed_message)
                    article_content = article_data["content"]
                    if not self.db.is_duplicate_article(article_data):
                        # 分析文章情緒
                        emotion = self.ai.analyze_emotion(article_content)
                        article_data["emotion"] = emotion
                        article_data["result_id"] = "init"
                        self.db.insert(article_data)
                    else:
                        logging.info(f"跳過重複文章：{article_data['title']}")

                embed_message = nextcord.Embed(
                    title=f"進度（{current_category}/**{total_categories}**）",
                    description=f"{title} 爬完了",
                    colour=nextcord.Color.gold()
                )
                await message.edit(f"{title} 版面的爬取完成（{current_category}/**{total_categories}**）",
                                   embed=embed_message)
                time.sleep(3)

            embed_message = nextcord.Embed(
                title="來自機器人的通知",
                description="爬取完成",
                colour=nextcord.Color.green()
            )
        await message.edit("", embed=embed_message)

    @nextcord.slash_command(description="choose specific ptt category and get emotion.",
                            guild_ids=GUILD_IDS)
    async def choose_a_category(self,
                                interaction: nextcord.Interaction,
                                category_name: str = SlashOption(
                                    name="categories",
                                    choices=board_categories(),
                                    required=True
                                ),
                                ):
        if interaction.user.id == self.bot.user.id:
            return
        channel = self.bot.get_channel(interaction.channel_id)
        async with channel.typing():
            embed_message = nextcord.Embed(
                title="爬取結果",
                description="正在爬取文章...",
                colour=nextcord.Color.red()
            )
            message = await interaction.send(embeds=[embed_message])
            message_id = interaction.channel.last_message_id
            hex_message_id = self.__encode_base64(message_id)
            response_url = f"{HOST_URL}/results/{hex_message_id}"

            articles_data = self.crawler.get_article_data(category_name, 1)

            for article_data in articles_data:
                embed_message = nextcord.Embed(
                    title="爬取結果",
                    description=f"正在判斷 **{article_data['title']}** 的情緒 ...",
                    colour=nextcord.Color.yellow()
                )
                article_content = article_data["content"]
                time.sleep(1)
                if self.db.is_duplicate_article(article_data):
                    emotion = self.ai.analyze_emotion(article_content)
                    article_data["emotion"] = emotion
                    article_data["result_id"] = hex_message_id
                    self.db.insert(article_data)
                else:
                    emotion = self.ai.analyze_emotion(article_content)
                    article_data["emotion"] = emotion
                    article_data["result_id"] = "init"
                    self.db.insert(article_data)
                    article_data["result_id"] = hex_message_id
                    self.db.insert(article_data)
                await message.edit(embeds=[embed_message])
        embed_message = nextcord.Embed(
            title="爬取結果",
            description=response_url,
            colour=nextcord.Color.green()
        )
        await message.edit(embed=embed_message)


def setup(bot):
    bot.add_cog(Crawler(bot))
