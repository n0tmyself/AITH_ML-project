

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import requests
import streamlit as st
from dotenv import load_dotenv
from streamlit_cookies_controller import CookieController
st.set_page_config(layout="wide")
load_dotenv()


BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
COOKIES_EXPIRE_DAYS = os.getenv("COOKIES_EXPIRE_DAYS", 14)
TOKEN_COOKIE_NAME = os.getenv("TOKEN_COOKIE_NAME")

st.markdown(
    """
    <style>
    /* Основной цвет кнопок */
    .stButton > button {
        background-color: #1a73e8;
        color: white;
        border: none;
        padding: 0.5em 1em;
        border-radius: 8px;
    }

    /* При наведении */
    .stButton > button:hover {
        background-color: #1558b0;
        color: white;
    }

    /* Чтобы кнопки занимали всю ширину, если задано use_container_width=True */
    .stButton > button:focus {
        outline: none;
        box-shadow: 0 0 0 3px rgba(26, 115, 232, 0.4);
    }
    </style>
    """,
    unsafe_allow_html=True
)



controller = CookieController()

if "username" not in st.session_state:
    st.session_state.username = None
if "balance" not in st.session_state:
    st.session_state.balance = 0
if "task_status" not in st.session_state:
    st.session_state.task_status = {}
if "show_topup" not in st.session_state:
    st.session_state.show_topup = False

models_price = {"lite": 5, "max": 20}


def register_user(username: str, email: str, password: str) -> Dict[str, Any]:
    response = requests.post(
        f"{BACKEND_URL}/auth/register",
        json={"name": username,"email": email, "password": password}
    )
    response.raise_for_status()
    return response.json()


def login_user(email: str, password: str) -> Dict[str, Any]:
    response = requests.post(f"{BACKEND_URL}/auth/login", json={"email": email, "password": password})
    response.raise_for_status()
    data: Dict[str, Any] = response.json()
    controller.set(
        TOKEN_COOKIE_NAME,
        data["access_token"],
        expires=datetime.now(timezone.utc) + timedelta(days=int(COOKIES_EXPIRE_DAYS)),
    )
    return data


def get_balance() -> Dict[str, Any]:
    headers = {"Authorization": f"Bearer {controller.get(TOKEN_COOKIE_NAME)}"}
    response = requests.get(f"{BACKEND_URL}/user/balance", headers=headers)
    response.raise_for_status()
    return response.json()


def top_up_balance(amount: float) -> Optional[Dict[str, Any]]:
    if amount <= 0:
        return None

    headers = {"Authorization": f"Bearer {controller.get(TOKEN_COOKIE_NAME)}"}
    response = requests.post(
        f"{BACKEND_URL}/user/balance?amount={amount}",
        headers=headers,
    )
    response.raise_for_status()
    return response.json()


def generate_text(prompt: str, tariff: str) -> Dict[str, Any]:
    headers = {"Authorization": f"Bearer {controller.get(TOKEN_COOKIE_NAME)}"}
    response = requests.post(
        f"{BACKEND_URL}/model/generate",
        json={"prompt": prompt, "tariff": tariff},
        headers=headers,
    )
    response.raise_for_status()
    return response.json()


def logout():
    st.session_state.username = None
    st.session_state.balance = 0
    st.session_state.task_status = {}
    controller.remove(TOKEN_COOKIE_NAME)
    st.success("Вы вышли из системы.")


def update_balance():
    try:
        result = get_balance()
        st.session_state.balance = result["balance"]
        st.session_state.email = result["email"]
        st.session_state.username = result["name"]
    except Exception:
        pass


def main_page():
    with st.sidebar:
        balance_placeholder = st.empty()
        balance_placeholder.markdown(f"### Баланс: {st.session_state.balance:.2f} 🏦")

        if st.button("Пополнить баланс 🤑", use_container_width=True):
            st.session_state.show_topup = not st.session_state.show_topup
        if st.session_state.show_topup:
            amount = st.number_input("Сумма пополнения:", min_value=0, step=10)
            if st.button("Подтвердить пополнение"):
                try:
                    result = top_up_balance(amount)
                    if result is not None:
                        st.success(f"Баланс пополнен. Новый баланс: {result['new_balance']}")
                    else:
                        st.error("Введенная сумма должна быть больше 0.")
                    update_balance()
                    balance_placeholder.markdown(f"### Баланс: {st.session_state.balance:.2f} 💰")
                except Exception as e:
                    st.error(f"Ошибка: {str(e)}")

        if st.button("Выйти", use_container_width=True):
            logout()
            st.rerun()

        tariff = st.selectbox("Tariff:", ["lite", "max"])

    st.title(f"Добро пожаловать, {st.session_state.username}!")
    prompt = st.text_area("Введите текст:", height=175)

    if st.button("Узнать про болезнь"):
        if st.session_state.balance < models_price[tariff]:
            st.error("Недостаточно средств")
        else:
            try:
                generation_result = generate_text(prompt, tariff)
                text_generation_task_status_placeholder = st.empty()
                text_generation_task_status_placeholder.success(f"Task id: {generation_result['task_id']}")

                update_balance()
                balance_placeholder.markdown(f"### Баланс: {st.session_state.balance:.2f} 💰")

                generated_text_placeholder = st.empty()
                generated_text_placeholder.code(generation_result["result"], language="text")
            except Exception as e:
                st.error(f"Ошибка при генерации: {str(e)}")


def auth_page():
    st.title("МедИИ")
    tab1, tab2 = st.tabs(["Регистрация", "Вход"])

    with tab1:
        username = st.text_input("Имя пользователя", key="reg_username")
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Пароль", type="password", key="reg_password")
        if st.button("Зарегистрироваться"):
            try:
                register_user(username, email, password)
                st.success("Успешно! Теперь можете войти в систему.")
            except Exception as e:
                st.error(f"Ошибка: {str(e)}")

    with tab2:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Пароль", type="password", key="login_password")
        if st.button("Войти"):
            try:
                login_user(email, password)
                update_balance()
                st.success("Успешный вход")
                st.rerun()
            except Exception as e:
                st.error(f"Ошибка: {str(e)}")


def app():
    if controller.get(TOKEN_COOKIE_NAME) is None:
        auth_page()
    else:
        main_page()
        update_balance()


if __name__ == "__main__":
    app()