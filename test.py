# max_perf_clicker_with_alert.py

import argparse
import time
from selenium.common.exceptions import NoAlertPresentException
from core.driver import init_driver
import config

def main(profile: str):
    driver = init_driver(profile)
    driver.get(config.URL)
    time.sleep(1)

    # границы из конфига
    sd, ed = config.DATE_START, config.DATE_END
    sh, eh = config.HOUR_START, config.HOUR_END

    # JS-инъекция без подавления alert/confirm
    js = f"""
    (function() {{
      const sd = '{sd}', ed = '{ed}', sh = {sh}, eh = {eh};
      setInterval(() => {{
        document
          .querySelectorAll('div.slot[data-timestamp]')
          .forEach(s => {{
            const ts = +s.getAttribute('data-timestamp');
            const d = new Date(ts*1000);
            const date = d.toISOString().slice(0,10), h = d.getHours();
            if (date >= sd && date <= ed && h >= sh && h <= eh) {{
              const r = s.querySelector('[data-btn_reload]');
              if (r) r.click();
              const btn = s.querySelector('button.btn-replace');
              if (btn && btn.textContent.trim()==='R') btn.click();
            }}
          }});
      }}, 10);
    }})();
    """
    driver.execute_script(js)

    try:
        while True:
            # проверяем наличие alert и подтверждаем
            try:
                alert = driver.switch_to.alert
                alert.accept()
            except NoAlertPresentException:
                pass

            # даём JS-интервалу пожить 10 ms до следующей проверки
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        driver.quit()

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('profile', help='имя папки профиля в profiles/')
    args = p.parse_args()
    main(args.profile)
