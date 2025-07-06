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
from selenium.webdriver.common.keys import Keys
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
    profile_path = os.path.expanduser(config.PROFILE_PATH)
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    if LOGGING:
        logger.info("WebDriver запущен успешно")
    return driver

def parse_timestamp(element):
    if LOGGING:
        logger.info("Парсинг timestamp из элемента")
    slot = element.find_element(By.XPATH, "./ancestor::div[contains(@class,'slot')]")
    ts = int(slot.get_attribute("data-timestamp"))
    if LOGGING:
        logger.info(f"Получен timestamp: {ts}")
    return ts

def in_desired_range(ts):
    dt = datetime.fromtimestamp(ts)
    date_str = dt.strftime("%Y-%m-%d")
    hour = dt.hour
    in_date = (config.DATE_START <= date_str <= config.DATE_END)
    in_hour = (config.HOUR_START <= hour <= config.HOUR_END)
    if LOGGING:
        logger.info(f"Проверка диапазона для {date_str} {hour:02d}:00 -> date_ok={in_date}, hour_ok={in_hour}")
    return in_date and in_hour

def confirm_alert(driver):
    if LOGGING:
        logger.info("Ожидание alert и подтверждение")
    WebDriverWait(driver, 5).until(EC.alert_is_present())
    alert = driver.switch_to.alert
    alert.send_keys(Keys.SPACE)
    if LOGGING:
        logger.info("Alert подтверждён")

def monitor():
    driver = init_driver()
    if LOGGING:
        logger.info(f"Открываем страницу: {config.URL}")
    driver.get(config.URL)
    if LOGGING:
        logger.info("Пауза 60 секунд для авторизации в браузере")
    time.sleep(120)
    if LOGGING:
        logger.info("Пауза завершена, начинаем мониторинг")
    while True:
        try:
            if LOGGING:
                logger.info("Ищем кнопки 'R'")
            candidates = driver.find_elements(
                By.XPATH,
                "//button[contains(@class,'btn-replace') and normalize-space(text())='R']"
            )
            for btn in candidates:
                ts = parse_timestamp(btn)
                if in_desired_range(ts):
                    if LOGGING:
                        logger.info(f"Найдена кнопка для ts={ts}, кликаем")
                    btn.click()
                    confirm_alert(driver)
                    logger.info("Смена захвачена, завершаем работу")
                    return
            if LOGGING:
                logger.info(f"Кнопки не найдены, обновляем через {config.REFRESH_INTERVAL}s")
            time.sleep(config.REFRESH_INTERVAL)
            driver.refresh()
        except UnexpectedAlertPresentException:
            if LOGGING:
                logger.info("UnexpectedAlertPresentException: подтверждаем alert")
            try:
                confirm_alert(driver)
            except Exception:
                pass
        except NoSuchElementException:
            if LOGGING:
                logger.info("NoSuchElementException: перезагрузка страницы")
            time.sleep(config.REFRESH_INTERVAL)
            driver.refresh()

if __name__ == "__main__":
    monitor()
