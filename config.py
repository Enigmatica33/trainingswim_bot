import os

from dotenv import load_dotenv

load_dotenv()

# SWIMMING_TOKEN = os.getenv('SWIMMING_TOKEN') # токен API с тренировками (база)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')  # токен бота TrainingSwimBot, который берет данные из базы тренировок
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')  # id Телеграм пользователя, подключившего бота и сделавшего запрос
# RETRY_PERIOD = 600
ENDPOINT = 'http://127.0.0.1:8000/api/tasks/'  # эндпойнт API с тренировками
# HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
