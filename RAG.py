from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from DeepSeekR1 import DeepSeekAPI
from dotenv import load_dotenv
import os

load_dotenv()

embeddings = HuggingFaceEmbeddings(
    model_name='sentence-transformers/all-MiniLM-L6-v2',
    model_kwargs={'device': 'cpu'},  
)

vector_store = Chroma(
    collection_name="wine_knowledge_db",
    embedding_function=embeddings,
    persist_directory="./wine_knowledge_db",
)

prompt_template = ChatPromptTemplate.from_template("""
    Ты - опытный сомелье, в задачу которого входит отвечать на вопросы пользователя про вина
    и рекомендовать лучшие вина к еде. Посмотри на всю имеющуюся в твоем распоряжении информацию
    и выдай одну или несколько лучших рекомендаций. Если что-то непонятно, то лучше уточни информацию
    у пользователя. Если ты не знаешь ответ, то просто скажи "Не знаю".

    Context: {context}

    Question: {question}

    Answer in detail:""")

llm = DeepSeekAPI(api_key=os.environ["DEEP_API_TOKEN"])

def ask_question(question):

    retrieved_docs = vector_store.similarity_search(question, k=3)
    docs_content = "\n".join([doc.page_content for doc in retrieved_docs])

    formatted_prompt = prompt_template.format(question=question, context=docs_content)

    answer = llm.ask(formatted_prompt)
    return answer

if __name__ == "__main__":
    question = "Какое вино подходит к стейку?"
    answer = ask_question(question)
    print("Question:", question)
    print("Answer:", answer)