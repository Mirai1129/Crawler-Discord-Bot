from datetime import datetime

from beanie import Document


class Ptt(Document):
    title: str
    content: str
    author: str
    link: str
    post_time: datetime
    generated_time: datetime
    emotion: str
    result_id: str

    class Settings:
        name = "ptt"
