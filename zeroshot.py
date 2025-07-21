from transformers import pipeline
from config import *


class ZeroShotClassifier:
    def __init__(self):
        # Используем zero-shot pipeline с моделью, поддерживающей мультиклассовую классификацию без дообучения
        self.classifier = pipeline("zero-shot-classification",
                                   model=MODEL_NAME)  # одна из популярных моделей для zero-shot

    def classify(self, text, candidate_labels):
        """
        Классифицирует текст на один из candidate_labels
        :param text: входной текст
        :param candidate_labels: список строк с метками классов, например ["спам", "заявка", "вопрос"]
        :return: наиболее вероятный класс
        """
        result = self.classifier(text, candidate_labels)
        # result — словарь с полями: 'sequence', 'labels', 'scores'

        '''output = {
            "text": text,
            "labels": result["labels"],
            "scores": result["scores"]
        }'''

        #return json.dumps(output, ensure_ascii=False, indent=2)
        return result["labels"][0]


class PromptedClassifier:
    def __init__(self):
        self.generator = pipeline("text2text-generation", model="google/flan-t5-base")

    def classify(self, text):
        prompt = f"Классифицируй текст по категориям: {', '.join(LABELS)}. Текст: {text}. Отвечай одним словом."
        output = self.generator(prompt, max_length=10)[0]['generated_text'].strip().lower()
        if output not in LABELS:
            return "неизвестно"
        return output

if __name__ == "__main__":
    model = PromptedClassifier()
    print(model.classify("Когда придёт мой заказ?"))