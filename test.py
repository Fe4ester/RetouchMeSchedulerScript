# max_perf_clicker_with_alert.py
# Скрипт для максимальной скорости обновления ячеек с корректной обработкой кнопки "R"
# Логика:
# 1. В браузер внедряется JS, который каждые 10ms перебирает ячейки и обновляет их,
#    и при появлении кнопки "R" кликает по ней, что вызывает стандартный alert.
# 2. alert блокирует дальнейшее выполнение JS-кода на таймере до нажатия "OK".
# 3. В Python запущен цикл, который каждые 10ms проверяет, есть ли активный alert,
#    и сразу его принимает, позволяя JS-интервалу продолжить работу.

import argparse
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoAlertPresentException
from core.driver import init_driver
import config


def main(profile: str):
    # 1) Инициализируем Chrome WebDriver с профилем пользователя
    driver = init_driver(profile)
    # 2) Переходим на страницу расписания смен
    driver.get(config.URL)
    # 3) Ждем 1 секунду, чтобы страница полностью загрузилась и отрисовалась
    time.sleep(1)

    # 4) Получаем из конфига границы: даты и часы для клика
    start_date = config.DATE_START  # строка 'YYYY-MM-DD'
    end_date = config.DATE_END      # строка 'YYYY-MM-DD'
    start_hour = config.HOUR_START  # целое число 0-23, локальный час
    end_hour = config.HOUR_END      # целое число 0-23, локальный час

    # 5) Подготавливаем JS-код для инъекции
    #    - setInterval с интервалом 10ms будет выполнять функцию
    #    - функция перебирает все div.slot с атрибутом data-timestamp
    #    - для каждого slot:
    #         * читаем timestamp (секунды с 1970)
    #         * создаем JS Date и получаем локальную дату и час
    #         * проверяем, попадает ли дата/час в нужный диапазон
    #         * если попадает:
    #             - сначала кликаем по кнопке reload (data-btn_reload), чтобы обновить содержимое ячейки
    #             - затем ищем появившуюся кнопку .btn-replace с текстом "R" и кликаем по ней,
    #               что вызывает стандартный alert в браузере
    js_code = f"""
    (function() {{
      const sd = '{start_date}';
      const ed = '{end_date}';
      const sh = {start_hour};
      const eh = {end_hour};
      // Запускаем интервал, который повторят функцию каждые 10ms
      setInterval(function() {{
        // Находим все слоты
        document.querySelectorAll('div.slot[data-timestamp]').forEach(function(slot) {{
          // Читаем timestamp и создаем дату
          const ts = Number(slot.getAttribute('data-timestamp'));
          const dt = new Date(ts * 1000);
          // Получаем строку даты "YYYY-MM-DD"
          const dateStr = dt.toISOString().slice(0,10);
          // Получаем локальный час из объекта Date
          const hour = dt.getHours();
          // Фильтр: только нужные даты и часы
          if (dateStr >= sd && dateStr <= ed && hour >= sh && hour <= eh) {{
            // 1) Принудительно обновляем ячейку: кликаем по reload-кнопке
            const reloadBtn = slot.querySelector('[data-btn_reload]');
            if (reloadBtn) {{ reloadBtn.click(); }}
            // 2) После обновления ищем кнопку "R" и кликаем по ней
            const reserveBtn = slot.querySelector('button.btn-replace');
            if (reserveBtn && reserveBtn.textContent.trim() === 'R') {{
              reserveBtn.click(); // это вызовет стандартный alert(), блокирующий JS
            }}
          }}
        }});
      }}, 10);
    }})();
    """

    # 6) Внедряем JS-код на страницу
    driver.execute_script(js_code)

    # 7) Цикл в Python для обработки alert
    try:
        while True:
            # Пытаемся переключиться на alert каждые 10ms
            try:
                alert = driver.switch_to.alert
                # Если alert появился, подтверждаем его через Python
                alert.accept()
            except NoAlertPresentException:
                # Если alert'а нет, продолжаем дальше без задержек
                pass
            # Небольшая пауза для снижения нагрузки на Python-цикл
            time.sleep(0.01)
    except KeyboardInterrupt:
        # Позволяет остановить скрипт Ctrl+C
        pass
    finally:
        # Корректно закрываем браузер
        driver.quit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Ультра-быстрый кликер с обработкой alert для R-слотов'
    )
    parser.add_argument('profile', help='имя папки профиля в profiles/')
    args = parser.parse_args()
    main(args.profile)
