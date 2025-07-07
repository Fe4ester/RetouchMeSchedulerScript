from pathlib import Path

# url не менять а то наебнется все
URL = "https://retouchme.com/backend2/duty/design/schedule"

DATE_START = "2025-07-08"
DATE_END = "2025-07-11"
HOUR_START = 14
HOUR_END = 23

OPEN_WINDOW = False
OPTIMISATION = False

PER_CELL_DELAY = 0.01

# профиля
BASE_DIR = Path(__file__).parent
PROFILES_DIR = BASE_DIR / "profiles"

# логи - для шарящих, так ставишь INFO
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"

TELEGRAM_BOT_TOKEN = "7866707915:AAFtP8ryM7Jzp8KpelkVNMaHcq8Kg_4BDYM"
TELEGRAM_CHAT_IDS = [690056650]