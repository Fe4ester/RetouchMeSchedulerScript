import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import config, logger


def init_driver(profile_name: str) -> webdriver.Chrome:
    profile_path = config.PROFILES_DIR / profile_name
    if not profile_path.exists():
        logger.logger.error(f"Профиля '{profile_name}' нет, выполните auth.py")
        raise FileNotFoundError(f"Profile {profile_name} not found")

    options = Options()
    options.add_argument(f"--user-data-dir={os.fspath(profile_path)}")
    options.add_argument("--headless=new")  # headless для скорости
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--blink-settings=imagesEnabled=false")  # без картинок

    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "eager"  # ждём только DOMContentLoaded

    driver = webdriver.Chrome(options=options, desired_capabilities=caps)
    logger.logger.info("WebDriver запущен в headless/eager режиме")
    return driver