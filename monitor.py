import threading
import time
import sys
import logger
import config
from core.driver import init_driver
from core.scraper import (
    find_replace_buttons,
    get_header_date_map,
    get_button_date_hour,
    should_take,
)
from selenium.common.exceptions import (
    NoSuchElementException,
    UnexpectedAlertPresentException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tg_bot import (
    start_bot,
    send_notification,
    send_failure_notification,
)


def confirm_alert(driver):
    WebDriverWait(driver, 5).until(EC.alert_is_present())
    driver.switch_to.alert.accept()


def is_login_page(driver) -> bool:
    return config.URL not in driver.current_url


def safe_click(driver, element):
    # Скроллим к элементу и кликаем, с fallback через JS
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    try:
        element.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", element)


def monitor(profile_name: str):
    driver = init_driver(profile_name)
    driver.get(config.URL)

    if is_login_page(driver):
        logger.logger.error("так ты войди сначала через auth.py")
        driver.quit()
        sys.exit(1)

    header_date_map = get_header_date_map(driver)
    logger.logger.info("Начинаем мониторинг...")
    taken = set()

    while True:
        try:
            buttons = find_replace_buttons(driver)
            for btn in buttons:
                # Пытаемся получить дату и час, пропуская stale-элементы
                try:
                    date_str, hour = get_button_date_hour(btn, header_date_map)
                except StaleElementReferenceException:
                    continue

                key = (date_str, hour)
                if key in taken:
                    logger.logger.debug(f"{key} уже захвачен")
                    continue

                if should_take(date_str, hour):
                    logger.logger.info(f"захватываем слот {key}")
                    try:
                        safe_click(driver, btn)
                        confirm_alert(driver)
                        taken.add(key)
                        logger.logger.info(f"слот захвачен {key}")
                        threading.Thread(
                            target=send_notification,
                            args=(date_str, hour, profile_name),
                            daemon=True
                        ).start()
                    except Exception as e:
                        logger.logger.error(f"Не удалось захватить слот {key}: {e}")
                        threading.Thread(
                            target=send_failure_notification,
                            args=(date_str, hour, profile_name, str(e)),
                            daemon=True
                        ).start()

            time.sleep(config.REFRESH_INTERVAL)
            # Частичное обновление таблицы через JS для скорости
            driver.execute_script("""
                fetch(arguments[0], {credentials:'include'})
                  .then(r=>r.text())
                  .then(html=>{
                      const doc=new DOMParser().parseFromString(html,'text/html');
                      const newTbl=doc.querySelector('table.schedule');
                      document.querySelector('table.schedule').replaceWith(newTbl);
                  });
            """, config.URL)

        except UnexpectedAlertPresentException:
            try:
                confirm_alert(driver)
            except:
                pass
        except NoSuchElementException:
            time.sleep(config.REFRESH_INTERVAL)
            driver.execute_script("location.reload();")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Мониторинг смен с Telegram")
    parser.add_argument("profile", type=str, help="имя профиля (папка в profiles/)")
    args = parser.parse_args()

    threading.Thread(target=start_bot, daemon=True).start()
    monitor(args.profile)
