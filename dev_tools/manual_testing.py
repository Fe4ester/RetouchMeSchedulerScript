# -*- coding: utf-8 -*-
"""
Manual tests для monitor.py — простые функции с выводом в терминал,
чтобы проверить, как работают основные части скрипта без доступа к сайту.
"""

import os
from datetime import datetime, timedelta
import main
import config


def test_init_driver():
    """
    Проверка инициализации WebDriver с профилем Chrome.
    Выводит, найдена ли папка профиля, и может ли Selenium запуститься.
    """
    profile = os.path.expanduser(config.PROFILE_PATH)  # тот же путь, что в main.init_driver
    if os.path.exists(profile):
        print(f"[OK] Папка профиля найдена: {profile}")
    else:
        print(f"[WARN] Папка профиля НЕ найдена: {profile}")

    try:
        driver = main.init_driver()
        print("[OK] Selenium WebDriver запущен успешно")
        driver.quit()
    except Exception as e:
        print("[FAIL] Ошибка при запуске WebDriver:", e)


def test_parse_timestamp():
    """
    Проверка parse_timestamp: проверяем, что из dummy-элемента
    извлекается правильный integer timestamp.
    """
    class DummySlot:
        def get_attribute(self, name):
            # эмулируем data-timestamp = 1620000000
            return '1620000000' if name == 'data-timestamp' else None

    class DummyElement:
        def find_element(self, by, expr):
            return DummySlot()

    el = DummyElement()
    ts = main.parse_timestamp(el)
    print(f"[OK] parse_timestamp вернул: {ts}")


def test_in_desired_range():
    """
    Проверка in_desired_range: точка внутри и вне диапазона.
    """
    # преобразуем строки config.DATE_* в дату
    start_date = datetime.strptime(config.DATE_START, "%Y-%m-%d")

    # точка внутри диапазона: тот же день, час = HOUR_START
    inside = start_date + timedelta(hours=config.HOUR_START)
    ts_inside = int(inside.timestamp())
    print("in_desired_range (должно True):", main.in_desired_range(ts_inside))

    # точка вне диапазона: день до DATE_START
    outside = start_date - timedelta(days=1)
    ts_outside = int(outside.timestamp())
    print("in_desired_range (должно False):", main.in_desired_range(ts_outside))


def test_confirm_alert():
    """
    Проверка confirm_alert:
    эмулируем driver с alert и печатаем, что нажали пробел.
    """
    # эмулируем WebDriverWait, чтобы не ждать реально
    original_wait = main.WebDriverWait
    class DummyWait:
        def __init__(self, driver, timeout): pass
        def until(self, cond): return True

    main.WebDriverWait = DummyWait

    class DummyAlert:
        def send_keys(self, key): print(f"[OK] send_keys вызван с: {key}")
        def accept(self): print("[OK] alert.accept() вызван")

    class DummyDriver:
        def __init__(self): self.switch_to = self
        @property
        def alert(self): return DummyAlert()

    drv = DummyDriver()
    main.confirm_alert(drv)
    # возвращаем оригинал
    main.WebDriverWait = original_wait


if __name__ == "__main__":
    print("=== Запуск тестов monitor.py ===")
    test_init_driver()
    # print()
    # test_parse_timestamp()
    # print()
    # test_in_desired_range()
    # print()
    # test_confirm_alert()
    print("=== Тесты завершены ===")
