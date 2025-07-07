import argparse
import time
from core.driver import init_driver
import config


def main(profile: str):
    # Инициализация WebDriver с указанным профилем
    driver = init_driver(profile)
    # Открываем страницу расписания
    driver.get(config.URL)
    # Ждем загрузки и рендеринга
    time.sleep(1)

    # Читаем из config диапазон дат и часов (локальных)
    start_date = config.DATE_START    # формат YYYY-MM-DD
    end_date = config.DATE_END        # формат YYYY-MM-DD
    start_hour = config.HOUR_START    # локальный час начала
    end_hour = config.HOUR_END        # локальный час конца

    # JS-код, который:
    # 1. Селектит все <div.slot data-timestamp>
    # 2. По timestamp создает Date, берет локальный час через .getHours()
    # 3. Фильтрует по дате и часу из config
    # 4. Кликает по кнопке [data-btn_reload] внутри ячейки
    js_clicker = f"""
    (function() {{
      const slots = document.querySelectorAll('div.slot[data-timestamp]');
      const sd = '{start_date}';
      const ed = '{end_date}';
      const sh = {start_hour};
      const eh = {end_hour};
      for (let s of slots) {{
        const ts = Number(s.getAttribute('data-timestamp'));
        const d = new Date(ts * 1000);
        const date = d.toISOString().slice(0,10);
        const h = d.getHours();  // локальный час вместо UTC
        if (date >= sd && date <= ed && h >= sh && h <= eh) {{
          const btn = s.querySelector('[data-btn_reload]');
          if (btn) btn.click();
        }}
      }}
    }})();
    """

    # Основной бесконечный цикл
    try:
        while True:
            # Запускаем JS-кликер, обновляем все ячейки за одну итерацию
            driver.execute_script(js_clicker)
            # Пауза между итерациями, можно уменьшить для большей частоты
            time.sleep(config.PER_CELL_DELAY)
    except KeyboardInterrupt:
        # Позволяет выйти по Ctrl+C без ошибок
        pass
    finally:
        # Закрываем драйвер корректно
        driver.quit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Max performance cell clicker script'
    )
    parser.add_argument(
        'profile',
        help='имя папки профиля в profiles/'
    )
    args = parser.parse_args()
    main(args.profile)