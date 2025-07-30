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

    def ask(self, text):
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": text}
            ]
        }

        response = requests.post(self.api_url, json=data, headers=self.headers)

        if response.status_code == 200:
            choices = response.json().get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "").strip()
            else:
                return "No response from model"
        else:
            return f"Error {response.status_code}: {response.text}"

    def classify(self, text):
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

    def collect_info(self, text):
        prompt = (
            f"Следующий текст является заявкой, которая потенциально должна принести компании прибыль\n"
            f"Твоя задача определить какие данные необходимо собрать у клиента, чтобы заполнить соответствующие поля"
            f"в базе данных, чтобы оформить заявку\n"
            f"Опрашивай клиента и уточняй у него всю необходимую информацию, чтобы в итоге получить следующие данные:\n"
            f"1. Суть сделки (обязательно)\n"
            f"Тип сделки (продажа / покупка / партнерство / услуга)\n"
            f"Что именно нужно (товар, услуга, инвестиции – кратко, например, поставка бетона, разработка сайта)\n"
            f"Бюджет или ожидаемая сумма (если клиент готов назвать)\n"
            f"2. Контактные данные (чтобы связаться)\n"
            f"Имя / Название компании\n"
            f"Телефон / Email (хотя бы что-то одно)\n"
            f"3. Дополнительно (если клиент сразу готов указать)\n"
            f"Сроки\n"
            f"Город / регион (если география важна)\n"
            f"Комментарий (любые уточнения от клиента)\n"
            f"Если какие-то данные сразу понятны из входного сообщения, то их спрашивать не нужно, "
            f"если о каких-то данных клиент упорно не говорит, то их нужно оставить пустыми\n"
            f"Текст:\n\"\"\"\n{text}\n\"\"\"\n"
            f"Ответь JSON в формате {{\"case_data\": все данные о клиенте и товаре текстовом виде}}."
            f"Никакий других данных в ответе быть не должно, только JSON, который можно распарсить"

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