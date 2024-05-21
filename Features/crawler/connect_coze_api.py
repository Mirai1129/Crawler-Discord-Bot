import requests
import json


def chat_with_bot(query):
    # 替換為你的個人訪問令牌和 Bot ID
    personal_access_token = '{}'
    bot_id = '{}'
    user_id = '{}'

    # 設置請求標頭
    headers = {
        'Authorization': f'Bearer {personal_access_token}',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Host': 'api.coze.com',
        'Connection': 'keep-alive'
    }

    # 設置請求數據
    data = {
        "conversation_id": "123",
        "bot_id": bot_id,
        "user": user_id,
        "query": query,
        "stream": False
    }

    try:
        # 發送 POST 請求
        response = requests.post('https://api.coze.com/open_api/v2/chat', headers=headers, data=json.dumps(data))
        response.raise_for_status()  # 檢查是否有HTTP錯誤

        # 解析和輸出回應
        response_data = response.json()
        print(f"Response JSON: {json.dumps(response_data, indent=2)}")  # 調試信息
        if response_data.get('code') == 0:
            messages = response_data.get('messages', [])
            if messages:
                for message in messages:
                    print(f"Bot: {message.get('content')}")
            else:
                print("沒有收到有效的回覆。")
        else:
            print(f"Error: {response_data.get('msg')}")
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Request Error: {err}")


if __name__ == "__main__":
    while True:
        user_input = input("請輸入您的問題: ")
        if user_input.lower() in ['exit', 'quit']:
            break
        chat_with_bot(user_input)
