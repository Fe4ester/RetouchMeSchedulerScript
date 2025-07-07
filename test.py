# test_click_cells.py

import argparse
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from selenium.webdriver.common.by import By
from core.driver import init_driver
import config

def ts_in_range(ts: int) -> bool:
    dt = datetime.fromtimestamp(ts)
    date_str = dt.strftime("%Y-%m-%d")
    hour = dt.hour
    return (config.DATE_START <= date_str <= config.DATE_END) and \
           (config.HOUR_START <= hour <= config.HOUR_END)

def click_slot(driver, slot_div):
    try:
        # скроллим ячейку в центр экрана
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            slot_div
        )
        time.sleep(0.02)

        # кликаем по кнопке reload внутри ячейки
        btn = slot_div.find_element(By.CSS_SELECTOR, "[data-btn_reload]")
        driver.execute_script("arguments[0].click();", btn)
    except Exception as e:
        print(f"Error clicking slot {slot_div.get_attribute('data-timestamp')}: {e}")

def main(profile):
    driver = init_driver(profile)
    driver.get(config.URL)
    time.sleep(1)  # ждём полной загрузки страницы

    # собираем все слоты в нужном диапазоне
    all_slots = driver.find_elements(By.CSS_SELECTOR, "div.slot[data-timestamp]")
    slots = []
    for div in all_slots:
        ts = int(div.get_attribute("data-timestamp"))
        if ts_in_range(ts):
            slots.append(div)

    print(f"Найдено {len(slots)} ячеек в диапазоне, кликаем...")

    # параллельно кликаем по всем ячейкам
    with ThreadPoolExecutor(max_workers=10) as exe:
        futures = [exe.submit(click_slot, driver, slot) for slot in slots]
        for f in as_completed(futures):
            pass  # можно обрабатывать результат, но нам не нужно

    print("Готово — все клики совершены.")
    time.sleep(2)
    driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Тест: параллельные клики по всем ячейкам в диапазоне"
    )
    parser.add_argument("profile", help="имя профиля (папка в profiles/)")
    args = parser.parse_args()
    main(args.profile)
