# max_perf_clicker.py
# Скрипт для максимально быстрого и оптимизированного клика по ячейкам
# Подход:
# 1) единым JS-запросом принудительно "рефрешим" все нужные ячейки
# 2) ждём, пока они загрузятся (config.PER_CELL_DELAY)
# 3) в течение config.PER_CELL_DELAY проверяем наличие кнопок "R", кликаем и подтверждаем alert
# 4) повторяем цикл

import argparse
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core.driver import init_driver
import config


def main(profile: str):
    # 1) Инициализация WebDriver с профилем
    driver = init_driver(profile)
    # 2) Открываем целевую страницу расписания
    driver.get(config.URL)
    # 3) Небольшая пауза для полной загрузки страницы
    time.sleep(1)

    # 4) Берём диапазон дат и часов из конфига
    sd = config.DATE_START    # YYYY-MM-DD
    ed = config.DATE_END      # YYYY-MM-DD
    sh = config.HOUR_START    # локальный час начала
    eh = config.HOUR_END      # локальный час конца

    # 5) JS-код для принудительного "рефреша" всех ячеек:
    #    - селектим <div.slot[data-timestamp]>
    #    - создаём Date по timestamp
    #    - фильтруем по дате и локальному часу
    #    - кликаем внутреннюю кнопку reload (data-btn_reload)
    js_reload = f"""
    (function() {{
      const slots = document.querySelectorAll('div.slot[data-timestamp]');
      for (let s of slots) {{
        const ts = Number(s.getAttribute('data-timestamp'));
        const d = new Date(ts * 1000);
        const date = d.toISOString().slice(0,10);
        const hour = d.getHours();
        if (date >= '{sd}' && date <= '{ed}' && hour >= {sh} && hour <= {eh}) {{
          const btn = s.querySelector('[data-btn_reload]');
          if (btn) btn.click();
        }}
      }}
    }})();
    """

    # Основной бесконечный цикл
    try:
        while True:
            # A) Принудительный рефреш всех ячеек одним JS-вызовом
            driver.execute_script(js_reload)
            # B) Ждём, пока ячейки прогрузятся
            time.sleep(config.PER_CELL_DELAY)

            # C) Ищем все кнопки "R" для захвата слотов
            buttons = driver.find_elements(
                By.XPATH,
                "//button[contains(@class,'btn-replace') and normalize-space(text())='R']"
            )
            # D) Кликаем по каждой найденной кнопке и подтверждаем alert
            for btn in buttons:
                try:
                    btn.click()  # жмём "R"
                    # ждём alert и подтверждаем
                    WebDriverWait(driver, 2).until(EC.alert_is_present())
                    driver.switch_to.alert.accept()
                except Exception:
                    # игнорируем, если нет alert или кнопка перестала быть валидной
                    pass

            # E) Пауза перед следующим циклом обновления
            time.sleep(config.PER_CELL_DELAY)

    except KeyboardInterrupt:
        # Остановка по Ctrl+C
        pass
    finally:
        # Корректное завершение работы драйвера
        driver.quit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Max performance cell clicker script'
    )
    parser.add_argument(
        'profile',
        help='имя папки профиля в profiles/'
    )
    args = parser.parse_args()
    main(args.profile)
