from typing_extensions import TypedDict
from typing import List, Dict, Any
from langgraph.graph import StateGraph, END
from DeepSeekR1 import DeepSeekAPI
from config import *
from aiogram import types
from database import UserMessagesDB
import json
import re

llm = DeepSeekAPI(DEEP_API_TOKEN)


def clean_json_string(raw_str: str) -> str:
    """
    Удаляет markdown-разметку вида:
    ```json
    {...}
    ```
    и возвращает чистый JSON внутри.
    Работает при наличии переносов и пробелов.
    """
    pattern = r"```json\s*(.*?)\s*```"
    match = re.search(pattern, raw_str, re.DOTALL | re.IGNORECASE)
    if match:
        cleaned = match.group(1).strip()
        print(f"[clean_json_string] Удалена обёртка. Результат:\n{cleaned}")
        return cleaned
    else:
        print("[clean_json_string] Обёртка не найдена, возвращаем строку как есть.")
        return raw_str.strip()


class GraphState(TypedDict):
    """Определение структуры состояния графа"""
    user: types.Message
    message: str  # Входное сообщение пользователя
    response: str  # Текущий ответ системы
    documents: List[str]  # Найденные документы (для вопросов)
    status: str  # Текущий статус обработки
    next_node: str  # Следующий узел для перехода
    collected_info: Dict[str, Any]


def classify_message(state: GraphState) -> Dict[str, Any]:
    """Классификация входящего сообщения"""
    message = state["message"]
    response = llm.classify(text=message).lower()

    if "спам" in response:
        print("Сообщение определено как спам")
        return {"status": "spam", "next_node": "END", "response": "Пожалуйста, не присылайте бессмысленные сообщения"}
    elif "заявка" in response:
        print("Сообщение определено как заявка")
        return {"status": "application", "next_node": "collect_info"}
    else:
        print("Сообщение определено как вопрос")
        return {"status": "question", "next_node": "retrieve"}


def retrieve(state: GraphState) -> Dict[str, Any]:
    """Поиск информации по вопросу"""
    print("retrieve")
    # Здесь должен быть реальный поиск документов
    return {
        "documents": ["Документ 1", "Документ 2"],
        "next_node": "grade_documents",
        "response": "Найдена информация по вашему вопросу"
    }


def grade_documents(state: GraphState) -> Dict[str, Any]:
    """Оценка релевантности документов"""
    print("grade_documents")
    return {
        "documents": state["documents"],
        "next_node": "generate",
        "response": "Документы проверены на релевантность"
    }


def generate(state: GraphState) -> Dict[str, Any]:
    """Генерация финального ответа"""
    print("generate")
    return {
        "response": f"{state['documents']}",
        "next_node": END
    }


def collect_info(state: GraphState) -> Dict[str, Any]:
    print("collect_info")
    collected_json_str = llm.collect_info(state["message"])
    print(f"collected_json_str (repr): {repr(collected_json_str)}")

    cleaned_json = clean_json_string(collected_json_str)
    print(f"Очищенный JSON-стринг:\n{cleaned_json}")

    try:
        collected_data = json.loads(cleaned_json)
        print(f"Распарсенные данные: {collected_data}")
    except json.JSONDecodeError as e:
        print(f"Ошибка при парсинге JSON: {e}")
        collected_data = {}

    return {
        "response": f"Благодарим за обращение, в ближайшее время с вами свяжутся!",
        "next_node": "save_to_db",
        "collected_info": collected_data
    }


async def save_to_db(state: GraphState) -> Dict[str, Any]:
    print("save_to_db")
    db = UserMessagesDB(DSN)
    await db.connect()
    await db.create_table()

    contact_info = state.get("collected_info", {}).get("contact_info")
    fio = state.get("collected_info", {}).get("fio")
    product = state.get("collected_info", {}).get("product")
    await db.save_message(state["user"], contact_info, fio, product)

    return {
        "status": "completed",
        "next_node": END
    }


# Создаем граф
workflow = StateGraph(GraphState)

# Добавляем узлы
workflow.add_node("classify", classify_message)
workflow.add_node("retrieve", retrieve)
workflow.add_node("grade_documents", grade_documents)
workflow.add_node("generate", generate)
workflow.add_node("collect_info", collect_info)
workflow.add_node("save_to_db", save_to_db)

# Устанавливаем начальную точку
workflow.set_entry_point("classify")

# Настраиваем условные переходы
workflow.add_conditional_edges(
    "classify",
    lambda state: state["next_node"],  # Переход по значению next_node
    {
        "retrieve": "retrieve",
        "collect_info": "collect_info",
        "END": END
    }
)

# Добавляем линейные переходы
workflow.add_edge("retrieve", "grade_documents")
workflow.add_edge("grade_documents", "generate")
workflow.add_edge("generate", END)
workflow.add_edge("collect_info", "save_to_db")
workflow.add_edge("save_to_db", END)

# Компилируем граф
graph = workflow.compile()

#graph_image = graph.get_graph().draw_mermaid_png()
#with open("../graph_image.png", "wb") as png:
    #png.write(graph_image)

async def run_agent(message: types.Message) -> str:
    """Асинхронный запуск агента для обработки сообщения"""
    inputs = {"user": message, "message": message.text, "collected_info": {}}
    last_response = "Не удалось обработать запрос."

    try:
        # Используем асинхронный поток графа
        async for output in graph.astream(inputs):
            if output:  # Если есть результат
                last_node = list(output.keys())[0]
                last_response = output[last_node].get("response", last_response)

        return last_response

    except Exception as e:
        print(f"Ошибка обработки: {e}")
        return "Произошла ошибка при обработке запроса"