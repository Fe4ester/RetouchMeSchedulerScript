import argparse
import time
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import InvalidSessionIdException
from core.driver import init_driver
import config
import logging


def main(profile: str):
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

    driver.get(config.URL)
    time.sleep(1)

    sd, ed = config.DATE_START, config.DATE_END
    sh, eh = config.HOUR_START, config.HOUR_END

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
    if(tsList.length===0) return;
    const ts=tsList.shift();
    tsList.push(ts);
    const sel=`div.slot[data-timestamp="${{ts}}"]`;
    const slot=document.querySelector(sel);
    if(slot) {{
      const r=slot.querySelector('[data-btn_reload]'); if(r) r.click();
      const btn=slot.querySelector('button.btn-replace');
      if(btn && btn.textContent.trim()==='R') btn.click();
    }}
  }}

  // мгновенный click по R через MutationObserver
  new MutationObserver(muts=>muts.forEach(m=>m.addedNodes.forEach(n=>{{
    if(n.nodeType===1 && n.matches('button.btn-replace') && n.textContent.trim()==='R') n.click();
  }}))).observe(
    document.querySelector('table.schedule tbody'),
    {{ childList:true, subtree:true }}
  );

  // основной цикл через setTimeout, чтобы избежать накопления интервалов
  function loop() {{
    reloadNext();
    const now=performance.now();
    if(now-lastRebuild>5*60*1000) buildList();
    setTimeout(loop, 5);
  }}

  // стартуем
  buildList();
  loop();
}})();
"""
    driver.execute_script(js)

    try:
        while True:
            try:
                alert = driver.switch_to.alert
                alert.accept()
                logging.info('Запиздючилась смена, чекай на сайте')
            except NoAlertPresentException:
                pass
            time.sleep(config.PER_CELL_DELAY)
    except (KeyboardInterrupt, InvalidSessionIdException):
        logging.error("упал браузер, завершаем")
    finally:
        driver.quit()


if __name__=='__main__':
    parser=argparse.ArgumentParser("хуй ебаный")
    parser.add_argument('profile', help='имя папки профиля в profiles/')
    args=parser.parse_args()
    main(args.profile)