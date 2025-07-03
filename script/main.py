import time
import os

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import config


def init_driver():
    options = Options()

    # example = "/Users/you/Library/Application Support/Google/Chrome/Default"
    profile_path = os.path.expanduser("~/any")

    options.add_argument(f"--user-data-dir={profile_path}")

    # после логина раскомментить

    # options.add_argument("--headless")

    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    return driver


def parse_timestamp(element):
    """
    забриает data timestamp у контейнера .slot
    """
    slot = element.find_element(By.XPATH, "./ancestor::div[contains(@class,'slot')]")
    ts = int(slot.get_attribute("data-timestamp"))
    return ts


def in_desired_range(ts):
    """
    сверка времегни и часа по указанному диапазону
    """
    dt = datetime.fromtimestamp(ts)
    # чекаем дату
    if not (config.DATE_START <= dt.strftime("%Y-%m-%d") <= config.DATE_END):
        return False
    # чекаем час
    if not (config.HOUR_START <= dt.hour <= config.HOUR_END):
        return False
    return True


def confirm_alert(driver):
    """
    получение и обработка алерта
    пока пробел, можно заменить на alert.accept()
    """
    WebDriverWait(driver, 5).until(EC.alert_is_present())
    alert = driver.switch_to.alert
    # эмулируем нажатие пробела
    alert.send_keys(Keys.SPACE)
    # или alert.accept()
    # alert.accept()


def monitor():
    driver = init_driver()
    driver.get(config.URL)

    while True:
        try:
            # ищем все кнопки R
            # по атрибуту data-btn_replace и тексту
            candidates = driver.find_elements(
                By.XPATH,
                "//button[contains(@class,'btn-replace') and normalize-space(text())='R']"
            )

            # фильтруем по диапазону
            for btn in candidates:
                ts = parse_timestamp(btn)
                if in_desired_range(ts):
                    btn.click()  # жмаем R
                    confirm_alert(driver)  # подтверждаем пробелом
                    print("Смена захвачена")
                    return

            # если ничего не нашли — ждём и обновляем
            time.sleep(config.REFRESH_INTERVAL)
            driver.refresh()

        except UnexpectedAlertPresentException:
            # если алерт выскочил - подтверждаем
            try:
                confirm_alert(driver)
            except:
                pass

        except NoSuchElementException:
            # в случае проблем с поиском элементов просто обновляем
            time.sleep(config.REFRESH_INTERVAL)
            driver.refresh()


if __name__ == "__main__":
    monitor()
