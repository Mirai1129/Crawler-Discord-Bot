import requests
import json
import os
from dotenv import load_dotenv  # 引入 dotenv 來加載 .env 文件

def chat_with_bot(query):
    load_dotenv() #呼叫載入 .env 檔
    personal_access_token = os.getenv("PERSONAL_ACCESS_TOKEN")
    bot_id = os.getenv("BOT_ID")

    headers = {
        'Authorization': f'Bearer {personal_access_token}',
        'Content-Type': 'application/json'
    }

    data = {
        "conversation_id": "123",
        "bot_id": bot_id,
        "user": "123333333",
        "query": query,
        "stream": False
    }

    try:
        response = requests.post('https://api.coze.com/open_api/v2/chat', headers=headers, data=json.dumps(data))
        response.raise_for_status()

        response_data = response.json()
        if response_data.get('code') == 0:
            for message in response_data.get('messages', []):
                if message.get('type') == 'answer':
                    return message.get('content')
            return "無效的回覆。"
        else:
            return f"Error: {response_data.get('msg')}"
    except requests.exceptions.RequestException as err:
        return f"Request Error: {err}"
