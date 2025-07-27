from dotenv import load_dotenv
import os
import logging

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
DB_URL = os.getenv("DB_URL")

def configure_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)03d] %(module)20s:%(lineno)-3d %(levelname)-8s - %(message)s"
    )