# -*- coding: utf-8 -*-
import time
import os
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import config

LOGGING = True
logger = logging.getLogger(__name__)
if LOGGING:
    logging.basicConfig(
        format='[%(asctime)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO
    )
else:
    logging.basicConfig(level=logging.WARNING)

def init_driver():
    if LOGGING:
        logger.info(f"Инициализация WebDriver с профилем: {config.PROFILE_PATH}")
    options = Options()
    options.add_argument(f"--user-data-dir={os.path.expanduser(config.PROFILE_PATH)}")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    if LOGGING:
        logger.info("WebDriver запущен успешно")
    return driver

def parse_timestamp(element):
    slot = element.find_element(By.XPATH, "./ancestor::div[contains(@class,'slot')]")
    return int(slot.get_attribute("data-timestamp"))

def in_desired_range(ts):
    dt = datetime.fromtimestamp(ts)
    date_str = dt.strftime("%Y-%m-%d")
    hour = dt.hour
    return (config.DATE_START <= date_str <= config.DATE_END) and (config.HOUR_START <= hour <= config.HOUR_END)

def confirm_alert(driver):
    WebDriverWait(driver, 5).until(EC.alert_is_present())
    alert = driver.switch_to.alert
    alert.accept()


def monitor():
    driver = init_driver()
    driver.get(config.URL)
    if LOGGING:
        logger.info("Пауза для авторизации (60s)")
    time.sleep(60)
    if LOGGING:
        logger.info("Начинаем мониторинг")

    taken_slots = set()
    while True:
        try:
            if LOGGING:
                logger.info("Ищем кнопки 'R'")
            buttons = driver.find_elements(
                By.XPATH,
                "//button[contains(@class,'btn-replace') and normalize-space(text())='R']"
            )
            for btn in buttons:
                ts = parse_timestamp(btn)
                dt = datetime.fromtimestamp(ts)
                key = (dt.strftime("%Y-%m-%d"), dt.hour)
                if not in_desired_range(ts):
                    continue
                if key in taken_slots:
                    if LOGGING:
                        logger.info(f"{key} уже захвачен, пропускаем")
                    continue
                if LOGGING:
                    logger.info(f"Захватываем смену для {key}")
                btn.click()
                confirm_alert(driver)
                taken_slots.add(key)
                if LOGGING:
                    logger.info(f"Смена захвачена для {key}")
            time.sleep(config.REFRESH_INTERVAL)
            driver.refresh()
        except UnexpectedAlertPresentException:
            try:
                confirm_alert(driver)
            except:
                pass
        except NoSuchElementException:
            time.sleep(config.REFRESH_INTERVAL)
            driver.refresh()

if __name__ == "__main__":
    monitor()
