# max_perf_clicker_with_alert.py
import argparse
import time
from selenium.common.exceptions import NoAlertPresentException
from core.driver import init_driver
import config

def main(profile: str):
    # 1) Инициализация WebDriver
    driver = init_driver(profile)

    # 1.1) Через CDP блокируем загрузку тяжёлых ресурсов (картинок, шрифтов, CSS)
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Network.setBlockedURLs", {
        "urls": ["*.png", "*.jpg", "*.jpeg", "*.svg", "*.css", "*.woff", "*.ttf"]
    })
    driver.execute_cdp_cmd("Network.setCacheDisabled", {"cacheDisabled": True})

    # 1.2) Отключаем CSS-анимации и переходы, чтобы рендер жил проще
    driver.execute_script("""
        document.body.style.animation = 'none';
        document.body.style.transition = 'none';
        document.querySelectorAll('*').forEach(el => {
            el.style.animation = 'none';
            el.style.transition = 'none';
        });
    """)

    # 2) Загружаем страницу расписания
    driver.get(config.URL)
    time.sleep(1)  # ждём полной отрисовки минимально

    # 3) Параметры из config
    sd = config.DATE_START
    ed = config.DATE_END
    sh = config.HOUR_START
    eh = config.HOUR_END

    # 4) JS-инъекция (MutationObserver + ротация + очистка раз в 5 минут)
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
        const ds = d.toISOString().slice(0,10);
        const h = d.getHours();
        return ds >= sd && ds <= ed && h >= sh && h <= eh;
      }});
    idx = 0;
  }}

  function reloadNext() {{
    if (!tsList.length) return;
    const ts = tsList[idx++ % tsList.length];
    const slot = document.querySelector(`div.slot[data-timestamp="${{ts}}"]`);
    if (!slot) return;
    const r = slot.querySelector('[data-btn_reload]');
    if (r) r.click();
    const btn = slot.querySelector('button.btn-replace');
    if (btn && btn.textContent.trim()==='R') btn.click();
  }}

  function startIntervals() {{
    reloadIntervalId = setInterval(reloadNext, 10);
    cleanupIntervalId = setInterval(() => {{
      clearInterval(reloadIntervalId);
      clearInterval(cleanupIntervalId);
      buildList();
      startIntervals();
    }}, 5*60*1000);
  }}

  new MutationObserver(muts => {{
    muts.forEach(m => {{
      m.addedNodes.forEach(node => {{
        if (node.nodeType===1 && node.matches('button.btn-replace') && node.textContent.trim()==='R') {{
          node.click();
        }}
      }});
    }});
  }}).observe(document.querySelector('table.schedule tbody'), {{ childList:true, subtree:true }});

  buildList();
  startIntervals();
}})();
"""
    driver.execute_script(js)

    # 5) Python-цикл: ловим и принимаем alert()
    try:
        while True:
            try:
                alert = driver.switch_to.alert
                alert.accept()
            except NoAlertPresentException:
                pass
            time.sleep(0.005)  # ждем 5ms
    except KeyboardInterrupt:
        pass
    finally:
        driver.quit()


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Clicker без утечек памяти, с оптимизацией CPU')
    p.add_argument('profile', help='имя папки профиля в profiles/')
    main(p.parse_args().profile)
