import telebot
import json
import schedule
import time
import threading
from datetime import datetime
from groq import Groq
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ===== НАЛАШТУВАННЯ =====
import os
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY"))
CONTACT = "@kilya117"
ADMIN_ID = 557881280
GROUP_CHAT_ID = None  # Буде встановлено через /getid в групі
# ========================

client = Groq(api_key=GROQ_API_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

admin_state = {}

# ==================== РОБОТА З ФАЙЛАМИ ====================

def load_db():
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(data):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_stats():
    with open("stats.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_stats(stats):
    with open("stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def load_config():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        config = {"group_chat_id": None, "news_schedule": [], "scheduled_news": []}
        save_config(config)
        return config

def save_config(config):
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def track_user(user_id, username):
    stats = load_stats()
    if user_id not in stats["users"]:
        stats["users"].append(user_id)
    stats["total_messages"] += 1
    save_stats(stats)

def track_section(section):
    stats = load_stats()
    if section in stats["section_clicks"]:
        stats["section_clicks"][section] += 1
    else:
        stats["section_clicks"][section] = 1
    save_stats(stats)

def track_ai_query(user_id, query):
    stats = load_stats()
    stats["ai_queries"].append({
        "user_id": user_id,
        "query": query[:100],
        "time": datetime.now().strftime("%d.%m.%Y %H:%M")
    })
    stats["ai_queries"] = stats["ai_queries"][-100:]
    save_stats(stats)

def is_admin(user_id):
    return user_id == ADMIN_ID

# ==================== РОЗСИЛКА НОВИН ====================

def send_scheduled_news():
    config = load_config()
    group_id = config.get("group_chat_id")
    if not group_id:
        print("Група не налаштована — розсилку пропущено")
        return
    news_list = config.get("scheduled_news", [])
    if not news_list:
        print("Немає новин для розсилки")
        return
    news = news_list[0]
    try:
        bot.send_message(group_id, f"📢 {news}")
        config["scheduled_news"].pop(0)
        save_config(config)
        print(f"Новину відправлено: {news[:50]}")
    except Exception as e:
        print(f"Помилка розсилки: {e}")

def setup_schedule():
    config = load_config()
    schedule_times = config.get("news_schedule", ["09:00", "18:00"])
    schedule.clear()
    for t in schedule_times:
        schedule.every().day.at(t).do(send_scheduled_news)
        print(f"Розсилку налаштовано на {t}")

def run_scheduler():
    setup_schedule()
    while True:
        schedule.run_pending()
        time.sleep(30)

# Запускаємо планувальник у фоні
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

# ==================== МЕНЮ ====================

def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("💼 Працевлаштування", callback_data="menu_jobs"),
        InlineKeyboardButton("💰 Гранти та фінансування", callback_data="menu_grants"),
        InlineKeyboardButton("🎓 Освіта та навчання", callback_data="menu_education"),
        InlineKeyboardButton("🏢 Державні послуги", callback_data="menu_state"),
        InlineKeyboardButton("🏥 Реабілітація та підтримка", callback_data="menu_rehab"),
        InlineKeyboardButton("📍 Можливості Подільської громади", callback_data="menu_podilsk"),
        InlineKeyboardButton("🤖 Запитати AI-помічника", callback_data="menu_ai"),
        InlineKeyboardButton("📞 Контакти та підтримка", callback_data="menu_contacts")
    )
    return markup

def back_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅️ Головне меню", callback_data="back_main"))
    return markup

def jobs_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🔍 Всі вакансії", callback_data="jobs_all"),
        InlineKeyboardButton("📍 Подільська громада", callback_data="jobs_podilsk"),
        InlineKeyboardButton("🌐 Віддалена робота", callback_data="jobs_remote"),
        InlineKeyboardButton("🏛️ Державна служба", callback_data="jobs_gov"),
        InlineKeyboardButton("⚙️ Оборонна промисловість", callback_data="jobs_defense"),
        InlineKeyboardButton("💻 IT та AI напрямки", callback_data="jobs_it"),
        InlineKeyboardButton("🎓 Навчання та перекваліфікація", callback_data="jobs_training"),
        InlineKeyboardButton("⬅️ Головне меню", callback_data="back_main")
    )
    return markup

def grants_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🎖️ Гранти для ветеранів", callback_data="grants_veteran"),
        InlineKeyboardButton("👨‍👩‍👧 Гранти для сімей", callback_data="grants_family"),
        InlineKeyboardButton("🏪 Гранти на власну справу", callback_data="grants_business"),
        InlineKeyboardButton("🌍 Міжнародні гранти", callback_data="grants_international"),
        InlineKeyboardButton("📍 Місцеві програми", callback_data="grants_local"),
        InlineKeyboardButton("📋 Де шукати гранти", callback_data="grants_search"),
        InlineKeyboardButton("⬅️ Головне меню", callback_data="back_main")
    )
    return markup

def education_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("💻 IT та AI напрямки", callback_data="edu_it"),
        InlineKeyboardButton("🆓 Безкоштовні курси", callback_data="edu_free"),
        InlineKeyboardButton("🌍 Міжнародні програми", callback_data="edu_international"),
        InlineKeyboardButton("🔄 Перекваліфікація", callback_data="edu_retraining"),
        InlineKeyboardButton("⬅️ Головне меню", callback_data="back_main")
    )
    return markup

def admin_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("➕ Додати вакансію", callback_data="admin_add_vacancy"),
        InlineKeyboardButton("➕ Додати грант", callback_data="admin_add_grant"),
        InlineKeyboardButton("🗑️ Видалити вакансію", callback_data="admin_del_vacancy"),
        InlineKeyboardButton("🗑️ Видалити грант", callback_data="admin_del_grant"),
        InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
        InlineKeyboardButton("💬 AI-запити", callback_data="admin_ai_queries"),
        InlineKeyboardButton("📢 Розсилка в групу", callback_data="admin_broadcast"),
        InlineKeyboardButton("📰 Додати новину в чергу", callback_data="admin_add_news"),
        InlineKeyboardButton("⏰ Налаштувати розклад", callback_data="admin_set_schedule"),
        InlineKeyboardButton("📋 Список вакансій", callback_data="admin_list_vacancies"),
        InlineKeyboardButton("📋 Список грантів", callback_data="admin_list_grants")
    )
    return markup

# ==================== AI ====================

def ask_groq(user_message):
    db = load_db()
    context = f"""
База вакансій:
{json.dumps(db['vacancies'], ensure_ascii=False, indent=2)}

База грантів:
{json.dumps(db['grants'], ensure_ascii=False, indent=2)}

Запит користувача: {user_message}
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": f"""Ти — помічник для ветеранів та демобілізованих осіб в Україні.
Допомагаєш знаходити роботу, гранти, соціальні послуги та програми підтримки.
Відповідай ТІЛЬКИ українською мовою. Будь дружнім, конкретним та корисним.
Використовуй дані з бази знань. Не вигадуй посилань або сум.
Не використовуй символи * або _ у відповіді.
Відповідай стисло та по суті."""},
            {"role": "user", "content": context}
        ],
        max_tokens=1000
    )
    return response.choices[0].message.content

def format_vacancies(vacancies):
    if not vacancies:
        return "Вакансій за цим запитом не знайдено."
    text = ""
    for v in vacancies:
        text += f"📌 {v['title']}\n"
        text += f"📍 {v['location']}\n"
        text += f"📝 {v['description']}\n"
        text += f"🔗 {v['link']}\n"
        if v.get("contact"):
            text += f"📞 Контакт: {v['contact']}\n"
        text += "\n"
    return text

def format_grants(grants):
    if not grants:
        return "Грантів за цим запитом не знайдено."
    text = ""
    for g in grants:
        text += f"💰 {g['title']}\n"
        text += f"💵 Сума: {g['amount']}\n"
        text += f"👤 Для кого: {g['for']}\n"
        text += f"📝 {g['description']}\n"
        text += f"🔗 {g['link']}\n"
        if g.get("contact"):
            text += f"📞 Контакт: {g['contact']}\n"
        text += "\n"
    return text

@bot.message_handler(commands=["sendnow"])
def send_news_now(message):
    if not is_admin(message.from_user.id):
        return
    config = load_config()
    group_id = config.get("group_chat_id")
    news_queue = config.get("scheduled_news", [])
    
    if not group_id:
        bot.send_message(message.chat.id, "Групу/канал не налаштовано.")
        return
    
    if not news_queue:
        bot.send_message(message.chat.id, "Черга новин пуста. Додай новину командою /addnews")
        return
    
    try:
        news = news_queue[0]
        bot.send_message(group_id, news)
        config["scheduled_news"].pop(0)
        save_config(config)
        bot.send_message(message.chat.id, f"✅ Новину відправлено!\n\nВ черзі осталось: {len(config['scheduled_news'])}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Помилка: {str(e)}")

# ==================== КОМАНДИ ====================

@bot.message_handler(commands=["start"])
def send_welcome(message):
    track_user(message.from_user.id, message.from_user.username)
    text = (
        "Вітаю! Я — навігатор можливостей для ветеранів України.\n\n"
        "Тут ти знайдеш:\n"
        "— вакансії та платформи для пошуку роботи\n"
        "— гранти на відкриття бізнесу у 2026 році\n"
        "— державні послуги та соціальну підтримку\n"
        "— можливості Подільської громади\n"
        "— безкоштовне навчання та перекваліфікацію\n\n"
        "Оберіть розділ:"
    )
    bot.send_message(message.chat.id, text, reply_markup=main_menu())

@bot.message_handler(commands=["menu"])
def show_menu(message):
    bot.send_message(message.chat.id, "Головне меню:", reply_markup=main_menu())

@bot.message_handler(commands=["admin"])
def admin_panel(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "У вас немає доступу до адмін-панелі.")
        return
    config = load_config()
    group_id = config.get("group_chat_id")
    status = f"Група: {group_id}" if group_id else "Група: не налаштована (напиши /getid в групі)"
    bot.send_message(message.chat.id, f"Адмін-панель\n{status}", reply_markup=admin_menu())

@bot.message_handler(commands=["getid"])
def get_id(message):
    chat_id = message.chat.id
    chat_type = message.chat.type
    if chat_type in ["group", "supergroup"]:
        if is_admin(message.from_user.id):
            config = load_config()
            config["group_chat_id"] = chat_id
            save_config(config)
            bot.send_message(chat_id, f"Групу підключено! ID: {chat_id}")
            bot.send_message(ADMIN_ID, f"Групу підключено! ID: {chat_id}\nТепер розсилка працюватиме в цій групі.")
        else:
            bot.send_message(chat_id, f"ID цієї групи: {chat_id}")
    else:
        bot.send_message(chat_id, f"Твій ID: {chat_id}")

@bot.message_handler(commands=["test"])
def test_broadcast(message):
    if not is_admin(message.from_user.id):
        return
    config = load_config()
    group_id = config.get("group_chat_id")
    if not group_id:
        bot.send_message(message.chat.id, "Групу/канал не налаштовано. Команда /getid в групі/каналі.")
        return
    try:
        bot.send_message(group_id, "🤖 Тестове повідомлення від навігатора ветеранів. Все працює правильно!")
        bot.send_message(message.chat.id, "✅ Тестове повідомлення відправлено в групу!")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Помилка: {str(e)}")

@bot.message_handler(commands=["news"])
def manage_news(message):
    if not is_admin(message.from_user.id):
        return
    config = load_config()
    news_queue = config.get("scheduled_news", [])
    schedule_times = config.get("news_schedule", ["09:00", "18:00"])
    
    text = (
        f"📰 Керування розсилкою новин\n\n"
        f"В черзі: {len(news_queue)} повідомлень\n"
        f"Розклад розсилки: {', '.join(schedule_times)}\n\n"
        f"Для додавання новини — напиши:\n"
        f"/addnews текст новини\n\n"
        f"Для перегляду черги:\n"
        f"/viewnews"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=["addnews"])
def add_news_direct(message):
    if not is_admin(message.from_user.id):
        return
    news_text = message.text.replace("/addnews ", "").strip()
    if not news_text:
        bot.send_message(message.chat.id, "Напиши: /addnews текст новини")
        return
    
    config = load_config()
    if "scheduled_news" not in config:
        config["scheduled_news"] = []
    config["scheduled_news"].append(f"📢 {news_text}")
    save_config(config)
    
    queue_count = len(config["scheduled_news"])
    bot.send_message(
        message.chat.id,
        f"✅ Новину додано до черги!\n"
        f"В черзі тепер: {queue_count} повідомлень\n\n"
        f"Новини надсилатимуться о: {', '.join(config.get('news_schedule', ['09:00', '18:00']))}"
    )

@bot.message_handler(commands=["viewnews"])
def view_news_queue(message):
    if not is_admin(message.from_user.id):
        return
    config = load_config()
    news_queue = config.get("scheduled_news", [])
    
    if not news_queue:
        bot.send_message(message.chat.id, "Черга новин пуста.")
        return
    
    text = f"📰 Черга новин ({len(news_queue)} шт):\n\n"
    for i, news in enumerate(news_queue, 1):
        text += f"{i}. {news[:80]}\n\n"
    bot.send_message(message.chat.id, text)

# ==================== АДМІН CALLBACKS ====================

@bot.callback_query_handler(func=lambda call: call.data == "back_admin")
def back_admin(call):
    if not is_admin(call.from_user.id):
        return
    bot.edit_message_text("Адмін-панель:", call.message.chat.id, call.message.message_id, reply_markup=admin_menu())

@bot.callback_query_handler(func=lambda call: call.data == "admin_stats")
def admin_stats(call):
    if not is_admin(call.from_user.id):
        return
    stats = load_stats()
    sections_ua = {
        "menu_jobs": "💼 Працевлаштування",
        "menu_grants": "💰 Гранти",
        "menu_education": "🎓 Освіта",
        "menu_state": "🏢 Держпослуги",
        "menu_rehab": "🏥 Реабілітація",
        "menu_podilsk": "📍 Подільська громада",
        "menu_ai": "🤖 AI-помічник",
        "menu_contacts": "📞 Контакти"
    }
    clicks_text = ""
    sorted_sections = sorted(stats["section_clicks"].items(), key=lambda x: x[1], reverse=True)
    for key, count in sorted_sections:
        name = sections_ua.get(key, key)
        clicks_text += f"  {name}: {count}\n"
    text = (
        f"📊 Статистика бота\n\n"
        f"👥 Унікальних користувачів: {len(stats['users'])}\n"
        f"💬 Всього повідомлень: {stats['total_messages']}\n"
        f"🤖 Запитів до AI: {len(stats['ai_queries'])}\n\n"
        f"📈 Популярність розділів:\n{clicks_text}"
    )
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅️ Адмін-панель", callback_data="back_admin"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "admin_ai_queries")
def admin_ai_queries(call):
    if not is_admin(call.from_user.id):
        return
    stats = load_stats()
    queries = stats["ai_queries"][-10:]
    if not queries:
        text = "Запитів до AI ще не було."
    else:
        text = "💬 Останні 10 запитів до AI:\n\n"
        for i, q in enumerate(reversed(queries), 1):
            text += f"{i}. [{q['time']}]\n{q['query']}\n\n"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅️ Адмін-панель", callback_data="back_admin"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "admin_list_vacancies")
def admin_list_vacancies(call):
    if not is_admin(call.from_user.id):
        return
    db = load_db()
    text = "📋 Список вакансій:\n\n"
    for v in db["vacancies"]:
        text += f"ID {v['id']}: {v['title']}\n"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅️ Адмін-панель", callback_data="back_admin"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "admin_list_grants")
def admin_list_grants(call):
    if not is_admin(call.from_user.id):
        return
    db = load_db()
    text = "📋 Список грантів:\n\n"
    for g in db["grants"]:
        text += f"ID {g['id']}: {g['title']}\n"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅️ Адмін-панель", callback_data="back_admin"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "admin_add_vacancy")
def admin_add_vacancy_cb(call):
    if not is_admin(call.from_user.id):
        return
    admin_state[call.from_user.id] = {"action": "add_vacancy", "step": "title", "data": {}}
    bot.send_message(call.message.chat.id, "Додавання вакансії.\n\nКрок 1/5: Напиши назву вакансії:")

@bot.callback_query_handler(func=lambda call: call.data == "admin_add_grant")
def admin_add_grant_cb(call):
    if not is_admin(call.from_user.id):
        return
    admin_state[call.from_user.id] = {"action": "add_grant", "step": "title", "data": {}}
    bot.send_message(call.message.chat.id, "Додавання гранту.\n\nКрок 1/6: Напиши назву гранту:")

@bot.callback_query_handler(func=lambda call: call.data == "admin_del_vacancy")
def admin_del_vacancy_cb(call):
    if not is_admin(call.from_user.id):
        return
    admin_state[call.from_user.id] = {"action": "del_vacancy", "step": "id", "data": {}}
    db = load_db()
    text = "Список вакансій:\n\n"
    for v in db["vacancies"]:
        text += f"ID {v['id']}: {v['title']}\n"
    text += "\nНапиши ID вакансії для видалення:"
    bot.send_message(call.message.chat.id, text)

@bot.callback_query_handler(func=lambda call: call.data == "admin_del_grant")
def admin_del_grant_cb(call):
    if not is_admin(call.from_user.id):
        return
    admin_state[call.from_user.id] = {"action": "del_grant", "step": "id", "data": {}}
    db = load_db()
    text = "Список грантів:\n\n"
    for g in db["grants"]:
        text += f"ID {g['id']}: {g['title']}\n"
    text += "\nНапиши ID гранту для видалення:"
    bot.send_message(call.message.chat.id, text)

@bot.callback_query_handler(func=lambda call: call.data == "admin_broadcast")
def admin_broadcast_cb(call):
    if not is_admin(call.from_user.id):
        return
    admin_state[call.from_user.id] = {"action": "broadcast", "step": "text", "data": {}}
    bot.send_message(call.message.chat.id, "Напиши повідомлення для розсилки всім користувачам бота:")

@bot.callback_query_handler(func=lambda call: call.data == "admin_add_news")
def admin_add_news_cb(call):
    if not is_admin(call.from_user.id):
        return
    config = load_config()
    news_count = len(config.get("scheduled_news", []))
    times = config.get("news_schedule", ["09:00", "18:00"])
    admin_state[call.from_user.id] = {"action": "add_news", "step": "text", "data": {}}
    bot.send_message(
        call.message.chat.id,
        f"В черзі новин: {news_count} повідомлень\n"
        f"Розклад розсилки: {', '.join(times)}\n\n"
        f"Напиши текст новини для додавання в чергу:"
    )

@bot.callback_query_handler(func=lambda call: call.data == "admin_set_schedule")
def admin_set_schedule_cb(call):
    if not is_admin(call.from_user.id):
        return
    admin_state[call.from_user.id] = {"action": "set_schedule", "step": "times", "data": {}}
    config = load_config()
    current = config.get("news_schedule", ["09:00", "18:00"])
    bot.send_message(
        call.message.chat.id,
        f"Поточний розклад розсилки: {', '.join(current)}\n\n"
        f"Напиши новий розклад через кому (формат ГГ:ХХ).\n"
        f"Наприклад: 09:00, 13:00, 18:00"
    )

# ==================== ДІАЛОГ АДМІНА ====================

def handle_admin_dialog(message):
    user_id = message.from_user.id
    state = admin_state.get(user_id)
    if not state:
        return False

    action = state["action"]
    step = state["step"]
    text = message.text.strip()

    if action == "add_vacancy":
        if step == "title":
            state["data"]["title"] = text
            state["step"] = "location"
            bot.send_message(message.chat.id, "Крок 2/5: Місто або регіон:")
        elif step == "location":
            state["data"]["location"] = text
            state["step"] = "description"
            bot.send_message(message.chat.id, "Крок 3/5: Короткий опис:")
        elif step == "description":
            state["data"]["description"] = text
            state["step"] = "link"
            bot.send_message(message.chat.id, "Крок 4/5: Посилання (або 'немає'):")
        elif step == "link":
            state["data"]["link"] = text if text != "немає" else ""
            state["step"] = "contact"
            bot.send_message(message.chat.id, "Крок 5/5: Контакт (або 'немає'):")
        elif step == "contact":
            state["data"]["contact"] = text if text != "немає" else ""
            db = load_db()
            new_id = max([v["id"] for v in db["vacancies"]], default=0) + 1
            new_vacancy = {
                "id": new_id,
                "title": state["data"]["title"],
                "category": "general",
                "location": state["data"]["location"],
                "type": "local",
                "description": state["data"]["description"],
                "link": state["data"]["link"],
                "contact": state["data"]["contact"]
            }
            db["vacancies"].append(new_vacancy)
            save_db(db)
            del admin_state[user_id]
            bot.send_message(message.chat.id, f"Вакансію додано! ID: {new_id}\nНазва: {new_vacancy['title']}", reply_markup=admin_menu())
        return True

    elif action == "add_grant":
        if step == "title":
            state["data"]["title"] = text
            state["step"] = "amount"
            bot.send_message(message.chat.id, "Крок 2/6: Сума гранту:")
        elif step == "amount":
            state["data"]["amount"] = text
            state["step"] = "for_who"
            bot.send_message(message.chat.id, "Крок 3/6: Для кого:")
        elif step == "for_who":
            state["data"]["for"] = text
            state["step"] = "description"
            bot.send_message(message.chat.id, "Крок 4/6: Опис:")
        elif step == "description":
            state["data"]["description"] = text
            state["step"] = "link"
            bot.send_message(message.chat.id, "Крок 5/6: Посилання (або 'немає'):")
        elif step == "link":
            state["data"]["link"] = text if text != "немає" else ""
            state["step"] = "contact"
            bot.send_message(message.chat.id, "Крок 6/6: Контакт (або 'немає'):")
        elif step == "contact":
            state["data"]["contact"] = text if text != "немає" else ""
            db = load_db()
            new_id = max([g["id"] for g in db["grants"]], default=0) + 1
            new_grant = {
                "id": new_id,
                "title": state["data"]["title"],
                "category": "general",
                "amount": state["data"]["amount"],
                "for": state["data"]["for"],
                "description": state["data"]["description"],
                "link": state["data"]["link"],
                "contact": state["data"]["contact"]
            }
            db["grants"].append(new_grant)
            save_db(db)
            del admin_state[user_id]
            bot.send_message(message.chat.id, f"Грант додано! ID: {new_id}\nНазва: {new_grant['title']}", reply_markup=admin_menu())
        return True

    elif action == "del_vacancy":
        try:
            del_id = int(text)
            db = load_db()
            vacancy = next((v for v in db["vacancies"] if v["id"] == del_id), None)
            if vacancy:
                db["vacancies"] = [v for v in db["vacancies"] if v["id"] != del_id]
                save_db(db)
                del admin_state[user_id]
                bot.send_message(message.chat.id, f"Вакансію видалено: {vacancy['title']}", reply_markup=admin_menu())
            else:
                bot.send_message(message.chat.id, f"Вакансії з ID {del_id} не знайдено. Спробуй ще раз:")
        except ValueError:
            bot.send_message(message.chat.id, "Введи числовий ID:")
        return True

    elif action == "del_grant":
        try:
            del_id = int(text)
            db = load_db()
            grant = next((g for g in db["grants"] if g["id"] == del_id), None)
            if grant:
                db["grants"] = [g for g in db["grants"] if g["id"] != del_id]
                save_db(db)
                del admin_state[user_id]
                bot.send_message(message.chat.id, f"Грант видалено: {grant['title']}", reply_markup=admin_menu())
            else:
                bot.send_message(message.chat.id, f"Гранту з ID {del_id} не знайдено. Спробуй ще раз:")
        except ValueError:
            bot.send_message(message.chat.id, "Введи числовий ID:")
        return True

    elif action == "broadcast":
        stats = load_stats()
        sent = 0
        failed = 0
        for uid in stats["users"]:
            try:
                bot.send_message(uid, f"📢 Повідомлення від адміністратора:\n\n{text}")
                sent += 1
            except Exception:
                failed += 1
        del admin_state[user_id]
        bot.send_message(message.chat.id, f"Розсилку завершено.\nНадіслано: {sent}\nНе вдалося: {failed}", reply_markup=admin_menu())
        return True

    elif action == "add_news":
        config = load_config()
        if "scheduled_news" not in config:
            config["scheduled_news"] = []
        config["scheduled_news"].append(text)
        save_config(config)
        del admin_state[user_id]
        news_count = len(config["scheduled_news"])
        times = config.get("news_schedule", ["09:00", "18:00"])
        bot.send_message(
            message.chat.id,
            f"Новину додано до черги!\n"
            f"В черзі: {news_count} повідомлень\n"
            f"Розклад: {', '.join(times)}\n\n"
            f"Новини надсилатимуться автоматично за розкладом.",
            reply_markup=admin_menu()
        )
        return True

    elif action == "set_schedule":
        try:
            times = [t.strip() for t in text.split(",")]
            for t in times:
                datetime.strptime(t, "%H:%M")
            config = load_config()
            config["news_schedule"] = times
            save_config(config)
            setup_schedule()
            del admin_state[user_id]
            bot.send_message(
                message.chat.id,
                f"Розклад оновлено!\nНовини надсилатимуться о: {', '.join(times)}",
                reply_markup=admin_menu()
            )
        except ValueError:
            bot.send_message(message.chat.id, "Невірний формат. Введи час у форматі ГГ:ХХ через кому.\nНаприклад: 09:00, 18:00")
        return True

    return False

# ==================== ОСНОВНІ CALLBACKS ====================

@bot.callback_query_handler(func=lambda call: call.data == "back_main")
def back_to_main(call):
    bot.edit_message_text("Головне меню:", call.message.chat.id, call.message.message_id, reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: call.data == "menu_jobs")
def menu_jobs(call):
    track_section("menu_jobs")
    bot.edit_message_text("💼 Працевлаштування\n\nОберіть категорію:", call.message.chat.id, call.message.message_id, reply_markup=jobs_menu())

@bot.callback_query_handler(func=lambda call: call.data == "jobs_all")
def jobs_all(call):
    db = load_db()
    text = "💼 Всі платформи для пошуку роботи:\n\n" + format_vacancies(db["vacancies"])
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back_button())

@bot.callback_query_handler(func=lambda call: call.data == "jobs_podilsk")
def jobs_podilsk(call):
    db = load_db()
    vacancies = [v for v in db["vacancies"] if v["category"] == "podilsk"]
    text = "📍 Вакансії в Подільській громаді:\n\n" + format_vacancies(vacancies)
    text += f"\nДля отримання актуального списку: {CONTACT}"
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back_button())

@bot.callback_query_handler(func=lambda call: call.data == "jobs_remote")
def jobs_remote(call):
    db = load_db()
    vacancies = [v for v in db["vacancies"] if "remote" in v["type"]]
    text = "🌐 Платформи для пошуку віддаленої роботи:\n\n" + format_vacancies(vacancies)
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back_button())

@bot.callback_query_handler(func=lambda call: call.data == "jobs_gov")
def jobs_gov(call):
    db = load_db()
    vacancies = [v for v in db["vacancies"] if v["category"] == "government"]
    text = "🏛️ Вакансії державної служби:\n\n" + format_vacancies(vacancies)
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back_button())

@bot.callback_query_handler(func=lambda call: call.data == "jobs_defense")
def jobs_defense(call):
    db = load_db()
    vacancies = [v for v in db["vacancies"] if v["category"] == "defense"]
    text = "⚙️ Вакансії в оборонній промисловості:\n\n" + format_vacancies(vacancies)
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back_button())

@bot.callback_query_handler(func=lambda call: call.data == "jobs_it")
def jobs_it(call):
    db = load_db()
    vacancies = [v for v in db["vacancies"] if v["category"] == "it"]
    text = "💻 IT та AI напрямки:\n\n" + format_vacancies(vacancies)
    text += "\nПорада: якщо немає досвіду в IT — почни з безкоштовних курсів на Prometheus або Дія.Цифрова освіта."
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back_button())

@bot.callback_query_handler(func=lambda call: call.data == "jobs_training")
def jobs_training(call):
    db = load_db()
    text = "🎓 Навчання та перекваліфікація:\n\n"
    for e in db["education"]:
        text += f"📚 {e['title']}\n{e['description']}\n🔗 {e['link']}\n\n"
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back_button())

@bot.callback_query_handler(func=lambda call: call.data == "menu_grants")
def menu_grants(call):
    track_section("menu_grants")
    bot.edit_message_text("💰 Гранти та фінансування\n\nОберіть категорію:", call.message.chat.id, call.message.message_id, reply_markup=grants_menu())

@bot.callback_query_handler(func=lambda call: call.data == "grants_veteran")
def grants_veteran(call):
    db = load_db()
    grants = [g for g in db["grants"] if g["category"] == "veteran"]
    text = "🎖️ Гранти для ветеранів 2026:\n\n" + format_grants(grants)
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back_button())

@bot.callback_query_handler(func=lambda call: call.data == "grants_family")
def grants_family(call):
    text = (
        "👨‍👩‍👧 Гранти для членів сімей ветеранів:\n\n"
        "Програма Власна справа (Дія)\n"
        "Сума: від 250 000 грн\n"
        "Для кого: подружжя, батьки та повнолітні діти ветеранів, сім'ї загиблих захисників\n"
        "Для сімей загиблих — до 1 000 000 грн за умови створення робочих місць.\n"
        "Посилання: https://business.diia.gov.ua\n\n"
        f"Консультація: {CONTACT}"
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back_button())

@bot.callback_query_handler(func=lambda call: call.data == "grants_business")
def grants_business(call):
    db = load_db()
    grants = [g for g in db["grants"] if g["category"] in ["veteran", "general"]]
    text = "🏪 Гранти на власну справу:\n\n" + format_grants(grants)
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back_button())

@bot.callback_query_handler(func=lambda call: call.data == "grants_international")
def grants_international(call):
    db = load_db()
    grants = [g for g in db["grants"] if g["category"] == "international"]
    text = "🌍 Міжнародні гранти:\n\n" + format_grants(grants)
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back_button())

@bot.callback_query_handler(func=lambda call: call.data == "grants_local")
def grants_local(call):
    db = load_db()
    grants = [g for g in db["grants"] if g["category"] == "local"]
    text = "📍 Місцеві грантові програми:\n\n" + format_grants(grants)
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back_button())

@bot.callback_query_handler(func=lambda call: call.data == "grants_search")
def grants_search(call):
    text = (
        "📋 Де шукати гранти:\n\n"
        "Грант-маркет України\nhttps://grantmarket.org.ua\n\n"
        "GURT — гранти для ГО\nhttps://gurt.org.ua/news/grants/\n\n"
        "Дія.Бізнес\nhttps://business.diia.gov.ua\n\n"
        "Ветеранський фонд\nhttps://veteranfund.com.ua\n\n"
        f"Консультація: {CONTACT}"
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back_button())

@bot.callback_query_handler(func=lambda call: call.data == "menu_education")
def menu_education(call):
    track_section("menu_education")
    bot.edit_message_text("🎓 Освіта та навчання\n\nОберіть категорію:", call.message.chat.id, call.message.message_id, reply_markup=education_menu())

@bot.callback_query_handler(func=lambda call: call.data == "edu_free")
def edu_free(call):
    db = load_db()
    courses = [e for e in db["education"] if e["category"] == "free"]
    text = "🆓 Безкоштовні курси:\n\n"
    for c in courses:
        text += f"📚 {c['title']}\n{c['description']}\n🔗 {c['link']}\n\n"
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back_button())

@bot.callback_query_handler(func=lambda call: call.data == "edu_it")
def edu_it(call):
    text = (
        "💻 IT та AI напрямки — з чого почати:\n\n"
        "1. Дія.Цифрова освіта — безкоштовно\nhttps://osvita.diia.gov.ua\n\n"
        "2. Prometheus — безкоштовні IT-курси\nhttps://prometheus.org.ua\n\n"
        "3. IT-курси від ДСЗ — держава оплачує навчання\nhttps://www.dcz.gov.ua\n\n"
        "4. DOU Jobs — вакансії в IT після навчання\nhttps://jobs.dou.ua\n\n"
        "Порада: починай з Python або основ веброзробки — найбільший попит на ринку."
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back_button())

@bot.callback_query_handler(func=lambda call: call.data == "edu_international")
def edu_international(call):
    db = load_db()
    courses = [e for e in db["education"] if e["category"] == "international"]
    text = "🌍 Міжнародні освітні програми:\n\n"
    for c in courses:
        text += f"📚 {c['title']}\n{c['description']}\n🔗 {c['link']}\n\n"
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back_button())

@bot.callback_query_handler(func=lambda call: call.data == "edu_retraining")
def edu_retraining(call):
    text = (
        "🔄 Перекваліфікація для ветеранів:\n\n"
        "Державна служба зайнятості\n"
        "Безкоштовне навчання за направленням. Виплати на час навчання.\n"
        "https://www.dcz.gov.ua\n\n"
        "Дія.Цифрова освіта\n"
        "Понад 20 безкоштовних курсів для освоєння нової професії.\n"
        "https://osvita.diia.gov.ua\n\n"
        "Prometheus\n"
        "Сертифікаційні курси з різних напрямків.\n"
        "https://prometheus.org.ua"
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back_button())

@bot.callback_query_handler(func=lambda call: call.data == "menu_state")
def menu_state(call):
    track_section("menu_state")
    db = load_db()
    text = "🏢 Державні послуги:\n\n"
    for s in db["state_services"]:
        text += f"📌 {s['title']}\n{s['description']}\n🔗 {s['link']}\n\n"
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back_button())

@bot.callback_query_handler(func=lambda call: call.data == "menu_rehab")
def menu_rehab(call):
    track_section("menu_rehab")
    db = load_db()
    text = "🏥 Реабілітація та підтримка:\n\n"
    for r in db["rehabilitation"]:
        text += f"💙 {r['title']}\n{r['description']}\n"
        if r.get("contact"):
            text += f"📞 {r['contact']}\n"
        text += f"🔗 {r['link']}\n\n"
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back_button())

@bot.callback_query_handler(func=lambda call: call.data == "menu_podilsk")
def menu_podilsk(call):
    track_section("menu_podilsk")
    db = load_db()
    text = "📍 Можливості Подільської громади:\n\n"
    for p in db["podilsk"]:
        text += f"📌 {p['title']}\n{p['description']}\n"
        if p.get("link"):
            text += f"🔗 {p['link']}\n"
        if p.get("contact"):
            text += f"📞 Контакт: {p['contact']}\n"
        text += "\n"
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back_button())

@bot.callback_query_handler(func=lambda call: call.data == "menu_contacts")
def menu_contacts(call):
    track_section("menu_contacts")
    text = (
        "📞 Контакти та підтримка:\n\n"
        f"👤 Фахівець із супроводу ветеранів\n"
        f"Telegram: {CONTACT}\n\n"
        "📞 Психологічна допомога — 1548 (24/7, безкоштовно)\n\n"
        "📞 Урядова гаряча лінія — 1545\n\n"
        "🌐 Навігатор можливостей\nhttps://navigator.pryncyp.org/\n\n"
        "🌐 е-Ветеран\nhttps://eveteran.gov.ua\n\n"
        "🌐 Ветеранський фонд\nhttps://veteranfund.com.ua"
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back_button())

@bot.callback_query_handler(func=lambda call: call.data == "menu_ai")
def menu_ai(call):
    track_section("menu_ai")
    text = (
        "🤖 AI-помічник\n\n"
        "Напиши своє питання — і я відповім!\n\n"
        "Наприклад:\n"
        "— Хочу відкрити кав'ярню, які є гранти?\n"
        "— Які вакансії є для водія в Одеській області?\n"
        "— Як отримати статус учасника бойових дій?\n"
        "— Які курси є для перекваліфікації?"
    )
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅️ Головне меню", callback_data="back_main"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

# ==================== ТЕКСТОВІ ПОВІДОМЛЕННЯ ====================

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    track_user(message.from_user.id, message.from_user.username)

    if is_admin(message.from_user.id) and message.from_user.id in admin_state:
        handle_admin_dialog(message)
        return

    bot.send_chat_action(message.chat.id, "typing")
    try:
        track_ai_query(message.from_user.id, message.text)
        response = ask_groq(message.text)
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🏠 Головне меню", callback_data="back_main"))
        bot.send_message(message.chat.id, response, reply_markup=markup)
    except Exception as e:
        bot.send_message(message.chat.id, "Вибач, сталась помилка. Спробуй ще раз або напиши /menu")
        print(f"Помилка: {e}")

print("Бот запущено! Натисни Ctrl+C щоб зупинити.")
bot.polling(none_stop=True)
