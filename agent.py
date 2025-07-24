import operator
from typing_extensions import TypedDict
from typing import List, Annotated
from langgraph.graph import StateGraph, END

class GraphState(TypedDict):
    """
    Описание структуры данных состояния графа.
    Состояние графа - это словарь, содержащий информацию,
    которую мы хотим передавать и изменять в каждом узле графа.
    """

    question: str     # Вопрос пользователя
    generation: str   # LLM генерация
    web_search: str   # Двоичное решение о запуске веб-поиска
    max_retries: int  # Максимальное количество повторных попыток генерации
    answers: int      # Количество сгенерированных ответов
    loop_step: Annotated[int, operator.add]
    documents: List[str]  # Список найденных документов


def classify_message(state):
    pass

def retrieve(state):
    pass

def grade_documents(state):
    pass

def generate(state):
    pass

def collect_info_from_client(state):
    pass

def save_to_db(state):
    pass

def notify_manager(state):
    pass

workflow = StateGraph(GraphState)

# Определение узлов
# workflow.add_node("classify_message", classify_message)
workflow.add_node("retrieve", retrieve)
workflow.add_node("grade_documents", grade_documents)
workflow.add_node("generate", generate)
workflow.add_node("collect_info_from_client", collect_info_from_client)
workflow.add_node("save_to_db", save_to_db)
workflow.add_node("notify_manager", notify_manager)

workflow.set_conditional_entry_point(
    classify_message,
    {
        "spam": "save_to_db",
        "application": "collect_info_from_client",
        "question": "retrieve"
    },
)

workflow.add_edge("retrieve", "grade_documents")
workflow.add_edge("grade_documents", "generate")
workflow.add_edge("collect_info_from_client", "save_to_db")
workflow.add_edge("generate", END)
workflow.add_conditional_edges(
    "save_to_db",
    save_to_db,
    {
        "collect_info_from_client": "collect_info_from_client",
        "notify_manager": "notify_manager",
        "end": END,

    }
)
graph = workflow.compile()
from IPython.display import Image, display

# Компиляция графа


# Сохраняем картинку в файл
graph_image = graph.get_graph().draw_mermaid_png()
with open("../graph_image.png", "wb") as png:
    png.write(graph_image)