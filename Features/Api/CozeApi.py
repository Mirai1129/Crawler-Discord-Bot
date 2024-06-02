import json
import logging
import os

import requests
from dotenv import load_dotenv

load_dotenv()
COZE_PERSONAL_ACCESS_TOKEN = os.getenv("COZE_PERSONAL_ACCESS_TOKEN")
COZE_BOT_ID = os.getenv("COZE_BOT_ID")


class CozeApi:
    def __init__(self):
        self.headers = {
            'Authorization': f'Bearer {COZE_PERSONAL_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        self.data = {
            "conversation_id": "123",
            "bot_id": COZE_BOT_ID,
            "user": "123333333",
            "query": "",
            "stream": False
        }
        logging.basicConfig(level=logging.INFO, format='[COZE_API] %(message)s')

    def get_article_emoji(self, query) -> str:
        self.data['query'] = query
        try:
            response = requests.post(
                url='https://api.coze.com/open_api/v2/chat',
                headers=self.headers,
                data=json.dumps(self.data)
            )
            response.raise_for_status()
            response_data = response.json()

            if response_data.get('code') == 0:
                for message in response_data.get('messages', []):
                    if message.get('type') == 'answer':
                        return message.get('content')
                logging.error("invalid response")
                return "無效的回覆。"
            return f"Error: {response_data.get('msg')}"
        except requests.exceptions.RequestException as err:
            logging.error(err)
            return f"Request Error: {err}"


if __name__ == '__main__':
    file_name = __file__.split("\\")[-1].split(".")[0]
    logging.info(f"{file_name} has been loaded")
