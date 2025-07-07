# max_perf_clicker.py
# Скрипт для максимально быстрой работы: JS-инъекция с setInterval в браузере
import argparse
import time
from core.driver import init_driver
import config

def main(profile: str):
    # Инициализация WebDriver и загрузка страницы
    driver = init_driver(profile)
    driver.get(config.URL)
    time.sleep(1)  # ждем полной загрузки

    # Читаем диапазон из config
    sd = config.DATE_START  # YYYY-MM-DD
    ed = config.DATE_END    # YYYY-MM-DD
    sh = config.HOUR_START  # локальный час начала
    eh = config.HOUR_END    # локальный час конца

    # Формируем JS для инъекции:
    # - Отключаем alert/confirm, чтобы не блокировали клик
    # - Запускаем setInterval каждые 10ms
    # - Внутри: находим и кликаем по reload и сразу по R
    js = f"""
    (function() {{
      // Бесконечное авто-кликание внутри браузера
      window.alert = function(){{}};
      window.confirm = function(){{return true;}};
      const sd = '{sd}'; const ed = '{ed}';
      const sh = {sh}; const eh = {eh};
      setInterval(() => {{
        document.querySelectorAll('div.slot[data-timestamp]').forEach(s => {{
          const ts = +s.getAttribute('data-timestamp');
          const d = new Date(ts * 1000);
          const date = d.toISOString().slice(0,10);
          const h = d.getHours();
          if (date >= sd && date <= ed && h >= sh && h <= eh) {{
            // принудительный reload ячейки
            const r = s.querySelector('[data-btn_reload]');
            if (r) r.click();
            // если появилась кнопка R — кликаем
            const btn = s.querySelector('button.btn-replace');
            if (btn && btn.textContent.trim() === 'R') btn.click();
          }}
        }});
      }}, 10);
    }})();
    """

    # Вводим код в браузер
    driver.execute_script(js)

    try:
        # Держим Python-процесс живым до Ctrl+C
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        driver.quit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ultra-fast JS clicker')
    parser.add_argument('profile', help='имя папки профиля в profiles/')
    args = parser.parse_args()
    main(args.profile)
