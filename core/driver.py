import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logger
import config


def init_driver(profile_name: str) -> webdriver.Chrome:
    profile_path = config.PROFILES_DIR / profile_name
    if not profile_path.exists():
        logger.logger.error(f"профиля '{profile_name}' нет, даун авторизуйся сначала")
        raise FileNotFoundError(f"Profile {profile_name} not found")

    options = Options()
    options.add_argument(f"--user-data-dir={os.fspath(profile_path)}")
    if not config.OPEN_WINDOW:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")

    options.add_argument("--disable-usb")
    options.add_argument("--disable-usb-discovery")

    for flag in [
        "--disable-gcm",
        "--disable-sync",
        "--disable-push-api",
        "--disable-background-networking",
        "--disable-default-apps",
        "--disable-client-side-phishing-detection",
        "--disable-component-update",
        "--disable-extensions",
        "--disable-features=PushMessaging,NetworkService,NetworkServiceInProcess"
    ]:
        options.add_argument(flag)

    options.add_argument("--log-level=3")

    logger.logger.debug(f"стартануло с профиля {profile_path}")
    driver = webdriver.Chrome(options=options)
    logger.logger.info("стартануло, слава богам, не зря молился")
    return driver
