from pathlib import Path

# url не менять а то наебнется все
URL = "https://retouchme.com/backend2/duty/design/schedule"
DATE_START = "2025-07-08"
DATE_END = "2025-07-11"
HOUR_START = 14
HOUR_END = 23
REFRESH_INTERVAL = 0.2  # в секундах

# профиля
BASE_DIR = Path(__file__).parent
PROFILES_DIR = BASE_DIR / "profiles"

# логи - для шарящих, так ставишь ERROR
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"

#TELEGRAM_BOT_TOKEN = "7568200834:AAHtPK206UVEGlkkoS-3vhwJNlJYtMW0Dlk"
TELEGRAM_BOT_TOKEN = "7866707915:AAFtP8ryM7Jzp8KpelkVNMaHcq8Kg_4BDYM"
TELEGRAM_CHAT_IDS = [690056650]