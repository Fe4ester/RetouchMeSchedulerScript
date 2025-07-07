# test_click_cells_loop.py

import argparse
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from core.driver import init_driver
import config


def ts_in_range(ts: int) -> bool:
    dt = datetime.fromtimestamp(ts)
    date_str = dt.strftime("%Y-%m-%d")
    hour = dt.hour
    return (config.DATE_START <= date_str <= config.DATE_END) and \
           (config.HOUR_START <= hour <= config.HOUR_END)


def click_slot_by_ts(driver, ts: str):
    try:
        # Найти ячейку по timestamp свежим селектором
        slot_div = driver.find_element(By.CSS_SELECTOR, f"div.slot[data-timestamp='{ts}']")
        # Прокручиваем в центр и кликаем reload-кнопку
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", slot_div)
        time.sleep(0.02)
        btn = slot_div.find_element(By.CSS_SELECTOR, "[data-btn_reload]")
        driver.execute_script("arguments[0].click();", btn)
    except StaleElementReferenceException:
        print(f"Stale element for timestamp {ts}, пропускаем")
    except Exception as e:
        print(f"Error clicking slot {ts}: {e}")


def main(profile: str):
    driver = init_driver(profile)
    driver.get(config.URL)
    time.sleep(1)

    print("Старт бесконечных кликов по всем ячейкам в диапазоне...")
    try:
        while True:
            # Сканируем текущие timestamps
            ts_list = []
            for div in driver.find_elements(By.CSS_SELECTOR, "div.slot[data-timestamp]"):
                try:
                    ts = div.get_attribute("data-timestamp")
                except StaleElementReferenceException:
                    continue
                if ts and ts_in_range(int(ts)):
                    ts_list.append(ts)

            if ts_list:
                # Параллельно кликаем по свежим элементам
                max_workers = min(len(ts_list), 10)
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = [executor.submit(click_slot_by_ts, driver, ts) for ts in ts_list]
                    for _ in as_completed(futures):
                        pass

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
