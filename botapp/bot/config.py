import logging

TOKEN = "724103183:AAHFhvu0CSd0LQh6pC8bJFmT93ID2TQg0XY"

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
