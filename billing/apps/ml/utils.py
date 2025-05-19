import os

from dotenv import load_dotenv
from langchain_gigachat.chat_models import GigaChat

load_dotenv()

GIGA_API_KEY = os.getenv("GIGA_API_KEY")
SCOPE = os.getenv("SCOPE")
MODEL_NAMES = {
    "lite": "GigaChat",
    # "pro" : "GigaChat-Pro",
    "max": "GigaChat-Max",
}


def generate_text(promt: str, tariff: str) -> str:
    """
    Generate text using Ollama's Gemma models based on the selected tariff.

    Args:
        prompt (str): The input prompt for text generation
        tariff (str): The tariff level (standart, pro, or premium)

    Returns:
        str: Generated text response
    """
    system_prompt = f"""
Ты профессиональный эксперт в области медицинских заболеваний, который генерирует ответ на запрос пользователя.
Твоя задача - написать только очень понятное описание болезни и симптомов, на основе названия этой болезни.
Если ты не знаешь про болезнь ничего, то так и напиши, что не знаешь такую болезнь.
Вот сама болезнь {promt}
"""
    try:
        model_name = MODEL_NAMES.get(tariff)
        if not model_name:
            return "Error: invalid tariff"
        model = GigaChat(
            credentials=GIGA_API_KEY,
            scope=SCOPE,
            model=model_name,
            verify_ssl_certs=False,
            temperature=0.85,
        )
        response = model.invoke(system_prompt)
        if isinstance(response.content, bytes):
            return response.content.decode("utf-8")
        return str(response.content)
    except Exception as e:
        return f"Error generating text: {str(e)}"
