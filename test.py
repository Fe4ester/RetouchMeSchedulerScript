# max_perf_clicker_with_alert.py
# Оптимизированный скрипт без утечек памяти, с корректной синтаксической записью
import argparse
import time
from selenium.common.exceptions import NoAlertPresentException
from core.driver import init_driver
import config


def main(profile: str):
    # Инициализация WebDriver и загрузка страницы
    driver = init_driver(profile)
    driver.get(config.URL)
    time.sleep(1)  # ждем полной загрузки

    # Диапазоны из конфига
    sd = config.DATE_START  # 'YYYY-MM-DD'
    ed = config.DATE_END    # 'YYYY-MM-DD'
    sh = config.HOUR_START  # 0–23 локальный час начала
    eh = config.HOUR_END    # 0–23 локальный час конца

    # JS-инъекция: MutationObserver + ротационный reload + очистка интервалов
    js = f"""
(function() {{
  const sd = '{sd}', ed = '{ed}', sh = {sh}, eh = {eh};
  let tsList = [], idx = 0;
  let reloadIntervalId, cleanupIntervalId;

  function buildList() {{
    tsList = Array.from(document.querySelectorAll('div.slot[data-timestamp]'))
      .map(el => el.getAttribute('data-timestamp'))
      .filter(ts => {{
        const d = new Date(Number(ts) * 1000);
        const dateStr = d.toISOString().slice(0,10);
        const hour = d.getHours();
        return dateStr >= sd && dateStr <= ed && hour >= sh && hour <= eh;
      }});
    idx = 0;
  }}

  function reloadNext() {{
    if (tsList.length === 0) return;
    const ts = tsList[idx++ % tsList.length];
    const selector = 'div.slot[data-timestamp="' + ts + '"]';
    const slot = document.querySelector(selector);
    if (!slot) return;
    const reloadBtn = slot.querySelector('[data-btn_reload]');
    if (reloadBtn) reloadBtn.click();
    const reserveBtn = slot.querySelector('button.btn-replace');
    if (reserveBtn && reserveBtn.textContent.trim() === 'R') {{
      reserveBtn.click();
    }}
  }}

  function startIntervals() {{
    reloadIntervalId = setInterval(reloadNext, 10);
    cleanupIntervalId = setInterval(() => {{
      clearInterval(reloadIntervalId);
      clearInterval(cleanupIntervalId);
      buildList();
      startIntervals();
    }}, 5 * 60 * 1000);
  }}

  // Обработчик появления кнопки R через MutationObserver
  const observer = new MutationObserver(mutations => {{
    for (const m of mutations) {{
      for (const node of m.addedNodes) {{
        if (node.nodeType === Node.ELEMENT_NODE) {{
          const el = node;
          if (el.matches('button.btn-replace') && el.textContent.trim() === 'R') {{
            el.click();
          }}
        }}
      }}
    }}
  }});
  const tbody = document.querySelector('table.schedule tbody');
  if (tbody) observer.observe(tbody, {{ childList: true, subtree: true }});

  // Запуск сборки списка и интервалов
  buildList();
  startIntervals();
}})();
"""

    # Внедрение JS-кода
    driver.execute_script(js)

    # Цикл Python для обработки alert
    try:
        while True:
            try:
                alert = driver.switch_to.alert
                alert.accept()
            except NoAlertPresentException:
                pass
            time.sleep(0.005)
    except KeyboardInterrupt:
        pass
    finally:
        driver.quit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Clicker без утечек памяти')
    parser.add_argument('profile', help='имя папки профиля в profiles/')
    args = parser.parse_args()
    main(args.profile)
