# max_perf_clicker_with_alert.py
# Ультрабыстрый визуальный кликер с логированием смен и Telegram-уведомлениями
import argparse
import time
import re
from selenium.common.exceptions import NoAlertPresentException
from core.driver import init_driver
from tg_bot import start_bot, send_notification, send_failure_notification
import config
import logger


def main(profile: str):
    # 1) Инициализация и оптимизация браузера
    driver = init_driver(profile)
    if config.OPTIMISATION:
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd("Network.setBlockedURLs", {"urls": [
            "*.png", "*.jpg", "*.jpeg", "*.svg", "*.css", "*.woff", "*.ttf"
        ]})
        driver.execute_cdp_cmd("Network.setCacheDisabled", {"cacheDisabled": True})
        driver.execute_script(
            "document.querySelectorAll('*').forEach(e=>{e.style.transition='none'; e.style.animation='none';});"
        )

    # 2) Открываем страницу и ждём базовую отрисовку
    driver.get(config.URL)
    time.sleep(1)

    # 3) Параметры из конфига
    sd, ed = config.DATE_START, config.DATE_END
    sh, eh = config.HOUR_START, config.HOUR_END

    # 4) JS-инъекция: MutationObserver + кольцевой цикл обновления
    js = f"""
(function() {{
  const sd='{sd}', ed='{ed}', sh={sh}, eh={eh};
  let tsList=[], lastRebuild=0;

  function buildList() {{
    tsList = Array.from(document.querySelectorAll('div.slot[data-timestamp]'))
      .map(el=>el.getAttribute('data-timestamp'))
      .filter(ts=>{{
        const d=new Date(+ts*1000);
        const ds=d.toISOString().slice(0,10), h=d.getHours();
        return ds>=sd && ds<=ed && h>=sh && h<=eh;
      }});
    lastRebuild = performance.now();
  }}

  function reloadNext() {{
    if(!tsList.length) return;
    const ts=tsList.shift(); tsList.push(ts);
    const slot=document.querySelector(`div.slot[data-timestamp="${{ts}}"]`);
    if(slot) {{
      const r=slot.querySelector('[data-btn_reload]'); if(r) r.click();
      const btn=slot.querySelector('button.btn-replace');
      if(btn && btn.textContent.trim()==='R') btn.click();
    }}
  }}

  new MutationObserver(muts=>muts.forEach(m=>m.addedNodes.forEach(n=>{{
    if(n.nodeType===1 && n.matches('button.btn-replace') && n.textContent.trim()==='R') n.click();
  }}))).observe(
    document.querySelector('table.schedule tbody'),
    {{ childList:true, subtree:true }}
  );

  function loop() {{
    reloadNext();
    if(performance.now()-lastRebuild>5*60*1000) buildList();
    setTimeout(loop, 5);
  }}

  buildList();
  loop();
}})();
"""
    driver.execute_script(js)

    # 5) Python-цикл: подтверждаем alert и рассылаем уведомления
    try:
        while True:
            try:
                alert = driver.switch_to.alert
                text = alert.text
                alert.accept()
                logger.logger.info(f"Слот захвачен: {text}")
                # Пытаемся распарсить дату и час из текста и отправить уведомление
                m = re.search(r"(\d{4}-\d{2}-\d{2}).* (\d+):00", text)
                if m:
                    date_str, hour = m.group(1), int(m.group(2))
                    send_notification(date_str, hour, profile)
                else:
                    # Если парсинг не удался, шлём общий текст
                    for cid in config.TELEGRAM_CHAT_IDS:
                        from tg_bot import bot
                        bot.send_message(cid, text)
            except NoAlertPresentException:
                pass
            time.sleep(config.PER_CELL_DELAY)
    except KeyboardInterrupt:
        pass
    finally:
        driver.quit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Clicker визуальный, быстрый и лёгкий')
    parser.add_argument('profile', help='имя папки профиля в profiles/')
    args = parser.parse_args()

    # Запуск Telegram-бота только один раз через lock-файл
    import os, errno

    lock_file = os.path.join(os.getcwd(), 'retouchme_bot.lock')
    try:
        fd = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_RDWR)
    except OSError as e:
        if e.errno == errno.EEXIST:
            logger.logger.info('Bot polling уже запущен, пропускаем.')
        else:
            raise
    else:
        from threading import Thread

        Thread(target=start_bot, daemon=True).start()

    main(args.profile)
