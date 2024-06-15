import os

import dotenv
from openai import OpenAI

dotenv.load_dotenv()


class OpenAIEmotionalAnalyzer:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def analyze_emotion(self, article_content):
        prompt = self._build_prompt(article_content)
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "你是一位專門分析文本情感的專家。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.5
        )
        return self._extract_emotion(response)

    @staticmethod
    def _build_prompt(article_content):
        return f"""
# 角色
你是一位審文的心理分析家，專門基於文章的標題和內容，評測並解析文章所蘊含的情感。

## 技能
### 技能1：評估文章情感
- 讀者提供任何文章時，你能即時說出文章的情感。

## 約束
- 依據文章，判斷並回答該文章所呈現的情感，你只能講情感本身，不得有多餘的回覆。
- 輸出內容中，你只能這樣回應 -> 傷心
- 僅能單一對應一個明確的情感 -> 開心
- 輸出內容不得有其他符號，只能有文字。

文章內容：
{article_content}
        """.strip()

    @staticmethod
    def _extract_emotion(response):
        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content.strip()
        else:
            return "無法分析情感"


# Example usage:
if __name__ == "__main__":
    article_content = """
    作者chen5651 (yo)
    看板happy
    標題[幸福] 星期五
    時間Fri May 17 19:16:07 2024

    最近忙到一個翻掉，今天終於告一個段落了
    快樂的點了三百的鹹酥雞和啤酒
    可惜食量不大好想再點燒烤！

    今天誰都不能阻止我！
    """.strip()

    analyzer = OpenAIEmotionalAnalyzer()
    emotion = analyzer.analyze_emotion(article_content)
    print("情感分析結果:", emotion)
