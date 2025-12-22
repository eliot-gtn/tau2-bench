from datetime import date, datetime

from tau2.utils.utils import DATA_DIR

PAYMENT_DATA_DIR = DATA_DIR / "tau2" / "domains" / "payment"

PAYMENT_DB_PATH = PAYMENT_DATA_DIR / "db.toml"
PAYMENT_USER_DB_PATH = PAYMENT_DATA_DIR / "user_db.toml"
PAYMENT_MAIN_POLICY_PATH = PAYMENT_DATA_DIR / "main_policy.md"

# TELECOM_TASK_SET_PATH_FULL = TELECOM_DATA_DIR / "tasks_full.json" # Not used anymore. Use full task split instead
# TELECOM_TASK_SET_PATH_SMALL = TELECOM_DATA_DIR / "tasks_small.json" # Not used anymore. Use small task split instead
PAYMENT_TASK_SET_PATH = PAYMENT_DATA_DIR / "tasks.json"


def get_now() -> datetime:
    # assume now is 2025-02-25 12:08:00
    return datetime(2025, 2, 25, 12, 8, 0)


def get_today() -> date:
    # assume today is 2025-02-25
    return date(2025, 2, 25)
