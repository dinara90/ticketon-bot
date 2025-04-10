import os
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

SEARCH_TERMS = ["Jennifer", "Lopez", "Дженнифер", "Лопес", "билет", "ticket"]
TRIGGER_TEXTS = ["Купить билет", "Buy ticket"]
EVENT_KEYWORDS = ["jennifer lopez", "дженнифер лопес"]

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text})
    except Exception as e:
        print("Ошибка отправки в Telegram:", e)

def search_ticket(term):
    search_url = f"https://ticketon.kz/search?q={term.replace(' ', '+')}"
    try:
        response = requests.get(search_url)
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", href=True)

        for link in links:
            text = link.get_text().lower()
            if any(keyword in text for keyword in EVENT_KEYWORDS):
                event_url = "https://ticketon.kz" + link["href"]
                print("🎯 Найдено мероприятие:", event_url)

                event_page = requests.get(event_url)
                event_soup = BeautifulSoup(event_page.text, "html.parser")
                full_text = event_soup.get_text().lower()

                if any(trigger.lower() in full_text for trigger in TRIGGER_TEXTS):
                    send_telegram(f"🎟 БИЛЕТЫ НАЙДЕНЫ! 👉 {event_url}")
                    return True
                else:
                    now = datetime.now().strftime('%H:%M:%S')
                    send_telegram(f"❌ Пока билетов нет (время: {now}). Ссылка найдена: {event_url}")
                    return False
        return False
    except Exception as e:
        send_telegram(f"⚠️ Ошибка при поиске '{term}': {e}")
        return False

# 🔁 Проверка каждые 5 минут
while True:
    found = False
    for term in SEARCH_TERMS:
        if search_ticket(term):
            found = True
            break

    if not found:
        now = datetime.now().strftime('%H:%M:%S')
        send_telegram(f"🔍 Бот проверил в {now}, ничего не найдено.")
        print(f"🔁 Проверка завершена в {now}")

    time.sleep(300)
