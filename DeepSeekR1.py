import requests

class DeepSeekAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.model = "deepseek/deepseek-r1:free"

    def ask(self, text, labels):
        labels_str = ", ".join(labels)
        prompt = (
            f"Проанализируй следующий текст и классифицируй его по одной из меток: заявка, вопрос или спам.\n"
            f"ВАЖНО, что эти сообщения адресуются конкретной компании и нерелевантные сообщения должны уходить в спам\n"
            f"К вопросам должны относиться только те сообщения, где пользователь хочет что-то узнать по тематике компании\n"
            f"К заявкам относятся сообщения, где видно, что пользователь хочет что-то купить, как-то проинвестировать или принести иную прбыль компании\n"
            f"Текст:\n\"\"\"\n{text}\n\"\"\"\n"
            "Ответь только одним словом — одной меткой, без пояснений и дополнительного текста."
        )

        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(self.api_url, json=data, headers=self.headers)

        if response.status_code == 200:
            choices = response.json().get("choices", [])
            if choices:
                # Уберём лишние пробелы и перейдём на нижний регистр (по необходимости)
                label = choices[0].get("message", {}).get("content", "").strip()
                return label
            else:
                return "Нет ответа от модели"
        else:
            return f"Ошибка {response.status_code}: {response.text}"