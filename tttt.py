import argparse
import config
from tg_bot import send_notification

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Тест уведомлений бота')
    parser.add_argument('--date', type=str, default=config.DATE_START, help='Дата в формате YYYY-MM-DD')
    parser.add_argument('--hour', type=int, default=config.HOUR_START, help='Час (0-23)')
    parser.add_argument('--profile', type=str, default='test', help='Имя профиля для вывода в сообщении')
    args = parser.parse_args()

    # Отправляем тестовое уведомление
    send_notification(args.date, args.hour, args.profile)
    print(f"Тестовое уведомление отправлено для {args.date} {args.hour}:00 (профиль: {args.profile})")
