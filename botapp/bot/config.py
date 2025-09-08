import logging

TOKEN = "8364479367:AAEgIA-whZJGZLHhhFN8b6-uZJ5W36zDWb4"

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
