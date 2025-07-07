# max_perf_clicker_with_alert.py
# Перепроектированный скрипт без утечек памяти:
# - Событийная обрабатка появления "R" через MutationObserver
# - Ротация перезагрузки слотов по индексу (без создания новых массивов каждый тик)
# - Периодическая чистка интервалов и пересборка структур для сброса памяти

import argparse
import time
from selenium.common.exceptions import NoAlertPresentException
from core.driver import init_driver
import config


def main(profile: str):
    # 1) Инициализируем драйвер и загружаем страницу
    driver = init_driver(profile)
    driver.get(config.URL)
    time.sleep(1)  # ждем полной загрузки

    # 2) Параметры из конфига
    sd = config.DATE_START  # 'YYYY-MM-DD'
    ed = config.DATE_END    # 'YYYY-MM-DD'
    sh = config.HOUR_START  # локальный час начала
    eh = config.HOUR_END    # локальный час конца

    # 3) JS-инъекция: комбинируем MutationObserver + ротационную перезагрузку + очистку каждые 5 минут
    js = f"""
(function() {{
  const sd = '{sd}', ed = '{ed}', sh = {sh}, eh = {eh};
  let tsList = [], idx = 0;
  let reloadIntervalId, cleanupIntervalId;

  function buildList() {{
    // Собираем timestamps нужных слотов
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
    const slot = document.querySelector(`div.slot[data-timestamp="${{ts}}"]`);
    if (!slot) return;
    // Перезагрузка слота
    const r = slot.querySelector('[data-btn_reload]');
    if (r) r.click();
    // Если показалась кнопка R — кликаем сразу и ждем alert
    const btn = slot.querySelector('button.btn-replace');
    if (btn && btn.textContent.trim() === 'R') btn.click();
  }}

  function startIntervals() {{
    // Перезагрузка каждого слота по одному каждые 10ms
    reloadIntervalId = setInterval(reloadNext, 10);
    // Каждые 5 минут чистим и пересоздаем список, чтобы освободить память
    cleanupIntervalId = setInterval(() => {{
      clearInterval(reloadIntervalId);
      buildList();
      startIntervals();
    }}, 5 * 60 * 1000);
  }}

  // 1) MutationObserver для мгновенного клика на R-слот
  const observer = new MutationObserver(muts => {{
    muts.forEach(m => {{
      m.addedNodes.forEach(node => {{
        if (node.matches && node.matches('button.btn-replace') && node.textContent.trim() === 'R') {{
          node.click();  // вызовет alert
        }}
      }});
    }});
  }});
  const tbody = document.querySelector('table.schedule tbody');
  observer.observe(tbody, {{ childList: true, subtree: true }});

  // 2) Инициализация списка и интервалов
  buildList();
  startIntervals();
  )();
"""

    driver.execute_script(js)

    # 4) Python-цикл для обработки alert, без задержек
    try:
        while True:
            try:
                alert = driver.switch_to.alert
                alert.accept()
            except NoAlertPresentException:
                pass
            time.sleep(0.005)  # проверяем чаще
    except KeyboardInterrupt:
        pass
    finally:
        driver.quit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Clicker with no memory leaks')
    parser.add_argument('profile', help='имя папки профиля в profiles/')
    args = parser.parse_args()
    main(args.profile)