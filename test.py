# max_perf_clicker_with_alert.py
# Улиtra-fast visual clicker без утечек памяти, уменьшенная нагрузка и увеличенная частота
import argparse
import time
from selenium.common.exceptions import NoAlertPresentException
from core.driver import init_driver
import config


def main(profile: str):
    # 1) Инициализация и лёгкие оптимизации браузера
    driver = init_driver(profile)
    # блокируем тяжёлые ресурсы через CDP

    # 2) Открываем страницу
    driver.get(config.URL)
    time.sleep(1)  # ждём базовую отрисовку

    # 3) Параметры из конфига
    sd, ed = config.DATE_START, config.DATE_END
    sh, eh = config.HOUR_START, config.HOUR_END

    # 4) JS: MutationObserver для R + синхронный setTimeout-цикл обновления
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

    # 5) Python-цикл для подтверждения alert
    try:
        while True:
            try:
                alert = driver.switch_to.alert
                alert.accept()
            except NoAlertPresentException:
                pass
            time.sleep(0.01)  # проверяем чаще при низкой нагрузке Python
    except KeyboardInterrupt:
        pass
    finally:
        driver.quit()


if __name__=='__main__':
    parser=argparse.ArgumentParser("Clicker визуальный, быстрый и лёгкий")
    parser.add_argument('profile', help='имя папки профиля в profiles/')
    args=parser.parse_args()
    main(args.profile)