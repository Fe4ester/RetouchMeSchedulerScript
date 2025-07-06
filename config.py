from pathlib import Path

# url не менять а то наебнется все
URL = "https://retouchme.com/backend2/duty/design/schedule"
DATE_START = "2025-07-06"
DATE_END = "2025-07-06"
HOUR_START = 18
HOUR_END = 18
REFRESH_INTERVAL = 0.2  # в секундах

# профиля
BASE_DIR = Path(__file__).parent
PROFILES_DIR = BASE_DIR / "profiles"

# логи - для шарящих, так ставишь ERROR
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"

TELEGRAM_BOT_TOKEN = "8191672504:AAHJQBuXID1SZXHTdHtQ3yAZlAk0VibrET0"
TELEGRAM_CHAT_IDS = [5899798915]
