import logging
import os
from datetime import datetime

os.makedirs("logs", exist_ok=True)

log_filename = os.path.join("logs", datetime.now().strftime("process_redmine_%Y-%m-%d_%H-%M-%S.log"))

logging.basicConfig(
    level=logging.NOTSET,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_filename),
    ]
)

logger = logging.getLogger("process_redmine")
