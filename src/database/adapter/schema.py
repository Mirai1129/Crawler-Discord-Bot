from typing import Any

from src.database.models import Ptt


async def insert_data(data: dict[str, Any]) -> Ptt:
    post = Ptt(**data)
    return await post.insert()


async def get_data(title: str,
                   author: str = None,
                   link: str = None,
                   result_id: str = None
                   ):
    query = {"title": title}

    if author:
        query["author"] = author
    if link:
        query["link"] = link
    if result_id:
        query["result_id"] = result_id

    return await Ptt.find(query).to_list()
