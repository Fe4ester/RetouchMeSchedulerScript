# test_click_cells_loop.py

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
        # Скроллим ячейку в центр и кликаем reload-кнопку
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            slot_div
        )
        btn = slot_div.find_element(By.CSS_SELECTOR, "[data-btn_reload]")
        driver.execute_script("arguments[0].click();", btn)
    except Exception as e:
        print(f"Error clicking slot {slot_div.get_attribute('data-timestamp')}: {e}")


def main(profile: str):
    driver = init_driver(profile)
    driver.get(config.URL)
    time.sleep(1)  # ждём полной загрузки

    print("Старт бесконечных кликов по всем ячейкам в диапазоне...")
    try:
        while True:
            # Сканируем слоты
            all_slots = driver.find_elements(By.CSS_SELECTOR, "div.slot[data-timestamp]")
            slots = [
                div for div in all_slots
                if ts_in_range(int(div.get_attribute("data-timestamp")))
            ]
            if slots:
                # Параллельно кликаем по всем найденным ячейкам
                with ThreadPoolExecutor(max_workers=len(slots)) as executor:
                    futures = [executor.submit(click_slot, driver, slot) for slot in slots]
                    for _ in as_completed(futures):
                        pass
            # Очень короткая пауза перед следующим циклом
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("Остановлено пользователем.")
    finally:
        driver.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Постоянные параллельные клики по ячейкам в диапазоне"
    )
    parser.add_argument(
        "profile",
        help="имя профиля (папка в profiles/)"
    )
    args = parser.parse_args()
    main(args.profile)
