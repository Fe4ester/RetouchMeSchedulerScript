import telebot
import config

bot = telebot.TeleBot(config.TELEGRAM_BOT_TOKEN)


@bot.message_handler(commands=['start', 'help'])
def cmd_start(message):
    bot.reply_to(
        message,
        "Бот уведомлений RetouchMeScheduler\n"
        "Чтобы получить свой chat_id, отправь команду /getid"
    )


@bot.message_handler(commands=['getid'])
def cmd_getid(message):
    bot.reply_to(
        message,
        f"Ваш chat_id: {message.chat.id}"
    )


@bot.message_handler(commands=['test'])
def cmd_test(message):
    bot.reply_to(
        message,
        "Это тестовое уведомление от RetouchMeScheduler"
    )


def start_bot(bot):
    bot.infinity_polling(timeout=10, long_polling_timeout=5)


def send_notification(date_str: str, hour: int, profile: str):
    from datetime import datetime
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    day_name = dt.strftime("%A")
    text = (
        f"<b>RetouchMeScheduler</b>\n"
        f"Профиль: <code>{profile}</code>\n"
        f"Слот захвачен: <b>{date_str} ({day_name})</b> в {hour}:00"
    )
    for chat_id in config.TELEGRAM_CHAT_IDS:
        try:
            bot.send_message(chat_id, text, parse_mode='HTML')
        except Exception as e:
            print(f"Ошибка отправки уведомления {chat_id}: {e}")