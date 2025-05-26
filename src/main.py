import asyncio
import logging
from datetime import datetime

from src.database import init_db
from src.database.adapter.schema import insert_data, get_data


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

async def main():
    await init_db()

    await insert_data({
        "title": "PTT 範例",
        "content": "這是一篇範例文章",
        "author": "gpt_user",
        "link": "https://www.ptt.cc/bbs/Example/M.12345678.A.html",
        "post_time": datetime.now(),
        "generated_time": datetime.now(),
        "emotion": "neutral",
        "result_id": "res-001"
    })

    posts = await get_data(title="PTT 範例")
    for post in posts:
        print(post.title)

if __name__ == "__main__":
    asyncio.run(main())
