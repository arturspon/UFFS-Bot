import os
from dotenv import load_dotenv

load_dotenv()

htciId = os.getenv('htciId')
htciKey = os.getenv('htciKey')
telegramToken = os.getenv('telegramToken')
databaseToken = os.getenv('DATABASE_URL')
