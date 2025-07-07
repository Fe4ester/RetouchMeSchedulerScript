# max_perf_clicker_with_alert.py
# Оптимизированный скрипт без утечек памяти, но с такой же скоростью работы
# Основная идея: собрать список ячеек один раз, сохранить их метаданные,
# и в интервале не выделять новые объекты (NodeList, Date и т.п.) каждый тик.

import argparse
import time
from selenium.common.exceptions import NoAlertPresentException
from core.driver import init_driver
import config


def main(profile: str):
    # 1) Инициализируем WebDriver и открываем страницу
    driver = init_driver(profile)
    driver.get(config.URL)
    time.sleep(1)  # ждём полной загрузки

    # 2) Берём диапазон из конфига
    sd = config.DATE_START  # 'YYYY-MM-DD'
    ed = config.DATE_END    # 'YYYY-MM-DD'
    sh = config.HOUR_START  # 0–23
    eh = config.HOUR_END    # 0–23

    # 3) Подготавливаем JS-код: один раз собираем слоты и их метаданные,
    #    и в setInterval (каждые 10ms) перебираем этот статический список.
    js_code = f"""
    (function() {{
      const sd = '{sd}', ed = '{ed}', sh = {sh}, eh = {eh};
      // Собираем слоты и метаданные единожды
      const rawSlots = Array.from(document.querySelectorAll('div.slot[data-timestamp]'));
      const slots = rawSlots.map(s => {{
        const ts = Number(s.getAttribute('data-timestamp'));
        const dt = new Date(ts * 1000);
        return {{ el: s, dateStr: dt.toISOString().slice(0,10), hour: dt.getHours() }};
      }});
      // Интервал: не создаём новых массивов или объектов, просто проходим по slots
      setInterval(() => {{
        for (let slot of slots) {{
          if (slot.dateStr >= sd && slot.dateStr <= ed &&
              slot.hour >= sh && slot.hour <= eh) {{
            // Пощелкать reload
            const r = slot.el.querySelector('[data-btn_reload]');
            if (r) r.click();
            // Если появилась кнопка R — зажать alert()
            const btn = slot.el.querySelector('button.btn-replace');
            if (btn && btn.textContent.trim() === 'R') btn.click();
          }}
        }}
      }}, 10);
    }})();
    """

    # 4) Выполняем инъекцию JS в страницу
    driver.execute_script(js_code)

    # 5) Python-цикл: ловим и подтверждаем alert каждую итерацию
    try:
        while True:
            try:
                alert = driver.switch_to.alert  # переключение на alert
                alert.accept()                 # подтверждаем
            except NoAlertPresentException:
                pass
            time.sleep(0.01)  # минимальная пауза
    except KeyboardInterrupt:
        # Ctrl+C — чистый выход
        pass
    finally:
        driver.quit()


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('profile', help='имя папки профиля в profiles/')
    args = p.parse_args()
    main(args.profile)