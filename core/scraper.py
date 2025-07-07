# core/scraper.py
import time
from selenium.webdriver.common.by import By
from datetime import datetime
import logger, config

def get_header_date_map(driver) -> dict[int, str]:
    headers = driver.find_elements(By.CSS_SELECTOR, "table.schedule thead th")[1:]
    date_map: dict[int, str] = {}
    current_year = datetime.now().year
    for idx, th in enumerate(headers, start=1):
        raw = th.text.splitlines()[0].strip()
        try:
            dt = datetime.strptime(f"{raw} {current_year}", "%d %b %Y")
            date_map[idx] = dt.strftime("%Y-%m-%d")
        except ValueError:
            logger.logger.warning(f"не удалось распарсить дату из заголовка: '{raw}'")
    return date_map

def build_views(driver):
    """Возвращает маппинги: колонки по дате и строки по часу."""
    headers = driver.find_elements(By.CSS_SELECTOR, "table.schedule thead th")[1:]
    # col_idx → WebElement th
    col_elems = {idx: el for idx, el in enumerate(headers, start=1)}
    # tbody tr: первый столбец — час, остальные — ячейки
    rows = driver.find_elements(By.CSS_SELECTOR, "table.schedule tbody tr")
    hour_rows = {}
    for row in rows:
        try:
            hour = int(row.find_element(By.TAG_NAME, "th").text.strip())
            hour_rows[hour] = row
        except:
            continue
    return col_elems, hour_rows

def click_and_try_cell(col_elem, row_elem):
    """Кликает по ячейке, ждёт загрузку и возвращает кнопку R, если она появилась."""
    # клик по заголовку колонки, чтобы lazy-load сработал
    col_elem.click()
    time.sleep(config.PER_CELL_DELAY)

    # сам td под этим заголовком:
    cells = row_elem.find_elements(By.TAG_NAME, "td")
    # т.к. col_elem индекс уже смещён на +1 из-за первой колонки часов
    idx = int(col_elem.get_attribute("cellIndex")) - 1
    if idx < 0 or idx >= len(cells):
        return None

    try:
        return cells[idx].find_element(
            By.XPATH,
            ".//button[contains(@class,'btn-replace') and normalize-space(text())='R']"
        )
    except:
        return None

# from selenium.webdriver.common.by import By
# from datetime import datetime
# import logger
# import config
#
#
# def get_header_date_map(driver) -> dict[int, str]:
#     # находим все <th> кроме первого (с часами)
#     headers = driver.find_elements(By.CSS_SELECTOR, "table.schedule thead th")[1:]
#     date_map: dict[int, str] = {}
#     current_year = datetime.now().year
#     for idx, th in enumerate(headers, start=1):
#         raw = th.text.splitlines()[0].strip()
#         try:
#             dt = datetime.strptime(f"{raw} {current_year}", "%d %b %Y")
#             date_map[idx] = dt.strftime("%Y-%m-%d")
#         except ValueError:
#             logger.logger.warning(f"не удалось распарсить дату из заголовка: '{raw}'")
#     return date_map
#
#
# def find_replace_buttons(driver) -> list:
#     xpath = (
#         "//button[contains(@class,'btn-replace') "
#         "and normalize-space(text())='R']"
#     )
#     return driver.find_elements(By.XPATH, xpath)
#
#
# def get_button_date_hour(button, header_date_map: dict[int, str]) -> tuple[str | None, int | None]:
#     # находим ячейку и её индекс столбца
#     cell = button.find_element(By.XPATH, "./ancestor::td")
#     try:
#         col_idx = int(cell.get_attribute("cellIndex"))
#     except (TypeError, ValueError):
#         logger.logger.error("не удалось получить индекс столбца для кнопки")
#         return None, None
#
#     date_str = header_date_map.get(col_idx)
#     # час из <th> той же строки
#     row = cell.find_element(By.XPATH, "./ancestor::tr")
#     try:
#         hour = int(row.find_element(By.TAG_NAME, "th").text.strip())
#     except ValueError:
#         hour = None
#     return date_str, hour
#
#
def should_take(date_str: str | None, hour: int | None) -> bool:
    if hour is None or date_str is None:
        return False
    if not (config.HOUR_START <= hour <= config.HOUR_END):
        logger.logger.debug(f"час {hour} вне диапазона {config.HOUR_START}-{config.HOUR_END}")
        return False
    if not (config.DATE_START <= date_str <= config.DATE_END):
        logger.logger.debug(f"дата {date_str} вне диапазона {config.DATE_START}-{config.DATE_END}")
        return False
    return True
