import threading, time, sys, logger, config
from core.driver import init_driver
from core.scraper import (
    get_header_date_map, build_views, click_and_try_cell, should_take
)
from selenium.common.exceptions import UnexpectedAlertPresentException, NoSuchElementException
from tg_bot import start_bot, send_notification, send_failure_notification


def confirm_alert(driver):
    try:
        driver.switch_to.alert.accept()
    except:
        pass


def monitor(profile_name: str):
    driver = init_driver(profile_name)
    driver.get(config.URL)

    # проверяем, вошли ли
    if config.URL not in driver.current_url:
        logger.logger.error("так ты войди сначала через auth.py")
        driver.quit();
        sys.exit(1)

    header_date_map = get_header_date_map(driver)
    col_elems, hour_rows = build_views(driver)
    logger.logger.info("Начинаем мониторинг быстрых кликов колонок/рядов...")

    taken = set()

    while True:
        try:
            # проходим по всем колонкам с нужными датами
            for col_idx, date_str in header_date_map.items():
                if not (config.DATE_START <= date_str <= config.DATE_END):
                    continue

                col_elem = col_elems[col_idx]

                # проходим по всем часам в нужном диапазоне
                for hour, row_elem in hour_rows.items():
                    key = (date_str, hour)
                    if key in taken or not (config.HOUR_START <= hour <= config.HOUR_END):
                        continue

                    btn = click_and_try_cell(col_elem, row_elem)
                    if not btn:
                        continue

                    # снова перепроверяем, что мы хотим этот слот
                    if should_take(date_str, hour):
                        logger.logger.info(f"захватываем слот {key}")
                        try:
                            btn.click()
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

            # небольшой отдых перед следующим циклом
            time.sleep(config.PER_CELL_DELAY)

        except UnexpectedAlertPresentException:
            confirm_alert(driver)
        except NoSuchElementException:
            time.sleep(config.PER_CELL_DELAY)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("profile", type=str, help="имя профиля (папка в profiles/)")
    args = parser.parse_args()

    threading.Thread(target=start_bot, daemon=True).start()
    monitor(args.profile)

# import threading
# import time
# import sys
# import logger
# import config
# from core.driver import init_driver
# from core.scraper import (
#     find_replace_buttons,
#     get_header_date_map,
#     get_button_date_hour,
#     should_take,
# )
# from selenium.common.exceptions import (
#     NoSuchElementException,
#     UnexpectedAlertPresentException,
# )
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
#
# from tg_bot import (
#     start_bot,
#     send_notification,
#     send_failure_notification,
# )
#
#
# def confirm_alert(driver):
#     WebDriverWait(driver, 5).until(EC.alert_is_present())
#     driver.switch_to.alert.accept()
#
#
# def is_login_page(driver) -> bool:
#     return config.URL not in driver.current_url
#
#
# def monitor(profile_name: str):
#     driver = init_driver(profile_name)
#     driver.get(config.URL)
#
#     if is_login_page(driver):
#         logger.logger.error("так ты войди сначала через auth.py")
#         driver.quit()
#         sys.exit(1)
#
#     header_date_map = get_header_date_map(driver)
#     logger.logger.info("Начинаем мониторинг...")
#     taken: set[tuple[str, int]] = set()
#
#     while True:
#         try:
#             buttons = find_replace_buttons(driver)
#             for btn in buttons:
#                 date_str, hour = get_button_date_hour(btn, header_date_map)
#                 key = (date_str, hour)
#
#                 if key in taken:
#                     logger.logger.debug(f"{key} уже захвачен")
#                     continue
#
#                 if should_take(date_str, hour):
#                     logger.logger.info(f"захватываем слот {key}")
#                     try:
#                         btn.click()
#                         confirm_alert(driver)
#                         taken.add(key)
#                         logger.logger.info(f"слот захвачен {key}")
#                         # уведомление об успехе
#                         threading.Thread(
#                             target=send_notification,
#                             args=(date_str, hour, profile_name),
#                             daemon=True
#                         ).start()
#                     except Exception as e:
#                         logger.logger.error(f"Не удалось захватить слот {key}: {e}")
#                         threading.Thread(
#                             target=send_failure_notification,
#                             args=(date_str, hour, profile_name, str(e)),
#                             daemon=True
#                         ).start()
#
#             time.sleep(config.REFRESH_INTERVAL)
#             driver.refresh()
#
#         except UnexpectedAlertPresentException:
#             try:
#                 confirm_alert(driver)
#             except:
#                 pass
#         except NoSuchElementException:
#             time.sleep(config.REFRESH_INTERVAL)
#             driver.refresh()
#
#
# if __name__ == "__main__":
#     import argparse
#
#     parser = argparse.ArgumentParser(description="Мониторинг смен с Telegram")
#     parser.add_argument(
#         "profile",
#         type=str,
#         help="имя профиля (папка в profiles/)"
#     )
#     args = parser.parse_args()
#
#     # старт бота в фоне
#     threading.Thread(target=start_bot, daemon=True).start()
#     # запуск мониторинга
#     monitor(args.profile)
