# 🪶 Проект "МедИИ"

## ℹ️ Информация о проекте

Биллинговый сервис с RAG - системой(пока что просто GigaChat) для генерации нужной медицинской информации. Пользователь может получить сведения о заболеваниях, симптомах, методах лечения и других аспектах здоровья, спросив обо всём, что его беспокоит в специальном чате. В проекте используется микросервисная архитектура.

## 🔑 Ключевые возможности

- Авторизация через JWT-токены 🔒
- Микросервисы для отделения клиентской части от моделей 🛠️
- Интегрированная система мониторинга: Prometheus + Grafana 📊

## 📱 UI

![Registration page](images/Registration.png)

![Registration_success](images/Registration_success.png)![Login](images/Login.png)![Main](images/Main.png)![Add_balance](images/Add_balance.png)

![Lite](images/Lite.png)

![Max](images/Max.png)

![Users](images/Users.png)

---

![Operations_1](images/Operations1.png)

![Operations2](images/Operations2.png)

![Balance_History](images/Balance_History.png)

![Balance_History](https://file+.vscode-resource.vscode-cdn.net/Users/dmitriy/Documents/GitHub/WorkSpace/AITH-ML-billing/images/Balance_History.png)

## ⚙️ Сервисы

- **backend 🌐**

  - FastAPI-приложение для аутентификации, маршрутизации и управления пользователями
  - Использует Redis в качестве брокера и backend-а для Celery
- **worker 🧠**

  - Получает задачи из Redis (через Celery)
  - Выполняет обработку и генерацию
- **frontend 🖼️**

  - Streamlit-интерфейс
  - Подключается к API по адресу `http://backend:8000`
- **reddis 🧩**

  - Хранилище задач и результатов для Celery
- **prometheus** & **grafana** 📈

  - Сбор и визуализация метрик по работе сервисов

## 🔎 Мониторинг

Метрики мониторинга собираются с помощью Grafana + Prometheus

![Мониторинг](docs/Grafana.png)

## 🚀 Запуск сервиса

> 1. `git clone https://github.com/n0tmyself/AITH-ML-project.git`
> 2. `cd AITH-ML-project && docker-compose up --build`
