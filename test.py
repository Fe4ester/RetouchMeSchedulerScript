# max_perf_clicker.py
# Скрипт для максимально быстрого параллельного клика по ячейкам в указанном диапазоне

import argparse
import time
from selenium.webdriver.common.by import By
from core.driver import init_driver
import config


def main(profile: str):
    # Инициализация WebDriver с заданным профилем
    driver = init_driver(profile)
    # Открываем целевую страницу
    driver.get(config.URL)
    # Ждём прогрева страницы после загрузки
    time.sleep(1)

    # Считываем границы диапазона из конфига
    start_date = config.DATE_START    # формат YYYY-MM-DD
    end_date = config.DATE_END        # формат YYYY-MM-DD
    start_hour = config.HOUR_START
    end_hour = config.HOUR_END

    # Пред-компилированный JS, который:
    # - Берёт все div.slot с data-timestamp
    # - Преобразует timestamp в дату (YYYY-MM-DD) и час (UTC)
    # - Фильтрует по диапазону дат и часов
    # - Кликает по внутренней кнопке [data-btn_reload]
    js_clicker = f"""
    const slots = document.querySelectorAll('div.slot[data-timestamp]');
    const sd = '{start_date}';
    const ed = '{end_date}';
    const sh = {start_hour};
    const eh = {end_hour};
    for (let s of slots) {{
        const ts = Number(s.getAttribute('data-timestamp'));
        const d = new Date(ts * 1000);
        const date = d.toISOString().slice(0,10);
        const h = d.getUTCHours();
        if (date >= sd && date <= ed && h >= sh && h <= eh) {{
            const btn = s.querySelector('[data-btn_reload]');
            if (btn) btn.click();
        }}
    }}
    """

    # Основной бесконечный цикл: исполняем JS-кликер и даём минимальную паузу
    try:
        while True:
            driver.execute_script(js_clicker)  # клик по всем нужным ячейкам
            time.sleep(0.01)                  # минимальная пауза
    except KeyboardInterrupt:
        # Остановка по Ctrl+C
        pass
    finally:
        # Корректное завершение работы драйвера
        driver.quit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Max performance cell clicker script'
    )
    parser.add_argument(
        'profile',
        help='имя папки профиля в profiles/'
    )
    args = parser.parse_args()
    main(args.profile)
