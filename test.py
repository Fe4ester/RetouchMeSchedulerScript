# max_perf_clicker_with_alert.py
# Оптимизированный скрипт без утечек и с постоянной работой
# Логика:
# 1. JS-инъекция собирает единожды список timestamps нужных ячеек (примитивы),
# 2. setInterval каждую итерацию по этому списку заново ищет элементы по timestamp,
#    не храня ссылки на DOM, чтобы избежать stale и утечек.
# 3. Для каждого timestamp: кликает reload и сразу проверяет наличие "R" кнопки,
#    кликает по ней и вызывает стандартный alert.
# 4. Python-цикл ловит и принимает alert, возобновляя JS-интервал.

import argparse
import time
from selenium.common.exceptions import NoAlertPresentException
from core.driver import init_driver
import config


def main(profile: str):
    # Инициализация и загрузка страницы
    driver = init_driver(profile)
    driver.get(config.URL)
    time.sleep(1)

    # Диапазон из конфига
    sd = config.DATE_START  # 'YYYY-MM-DD'
    ed = config.DATE_END    # 'YYYY-MM-DD'
    sh = config.HOUR_START  # 0-23 локальный час
    eh = config.HOUR_END    # 0-23 локальный час

    # JS-код
    js_code = f"""
    (function() {{
      const sd = '{sd}', ed = '{ed}', sh = {sh}, eh = {eh};
      // Собираем TS одной раз
      const tsList = Array.from(
        document.querySelectorAll('div.slot[data-timestamp]')
      )
      .map(el => el.getAttribute('data-timestamp'))
      .filter(ts => {{
        const d = new Date(Number(ts) * 1000);
        const dateStr = d.toISOString().slice(0,10);
        const hour = d.getHours();
        return dateStr >= sd && dateStr <= ed && hour >= sh && hour <= eh;
      }});
      // Основное авто-кликание
      setInterval(() => {{
        for (let ts of tsList) {{
          // Ищем элемент заново по timestamp каждый тик
          const selector = `div.slot[data-timestamp="${{ts}}"]`;
          const slot = document.querySelector(selector);
          if (!slot) continue;
          // 1) Reload
          const reloadBtn = slot.querySelector('[data-btn_reload]');
          if (reloadBtn) reloadBtn.click();
          // 2) Если кнопка R появилась - клик
          const reserveBtn = slot.querySelector('button.btn-replace');
          if (reserveBtn && reserveBtn.textContent.trim() === 'R') {{
            reserveBtn.click();  // вызовет alert()
          }}
        }}
      }}, 10);
    }})();
    """

    # Внедрение JS-инъекции
    driver.execute_script(js_code)

    try:
        # Обработка alert
        while True:
            try:
                alert = driver.switch_to.alert
                alert.accept()
            except NoAlertPresentException:
                pass
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass
    finally:
        driver.quit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Ultra-fast, leak-free clicker with alert handling'
    )
    parser.add_argument('profile', help='имя папки профиля в profiles/')
    args = parser.parse_args()
    main(args.profile)