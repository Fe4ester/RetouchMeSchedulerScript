import logger
import config
from core.driver import init_driver


def authenticate(profile_name: str):
    config.PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    profile_path = config.PROFILES_DIR / profile_name
    if not profile_path.exists():
        profile_path.mkdir(parents=True)
        logger.logger.info(f"создан профиль {profile_name}")

    driver = init_driver(profile_name)
    driver.get(config.URL)
    logger.logger.info(f"войди блять {config.URL} в профиле '{profile_name}'.")
    input("жми enter когда войдешь")
    driver.quit()
    logger.logger.info(f"добавил '{profile_name}'")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="аутентификация профиля")
    parser.add_argument(
        "profile",
        type=str,
        help="имя профиля (папка в profiles/)"
    )
    args = parser.parse_args()
    authenticate(args.profile)