import logging
import random
import sys

import requests
from telebot import TeleBot, types

from config import ENDPOINT, TELEGRAM_BOT_TOKEN
from constants import (
    COOLDOWN,
    COOLDOWN_DISTANCE,
    HELLO,
    LEVEL_PARAMETERS
)
from exceptions import MissingTokens
from logic import find_combinations
from saving_pdf import create_pdf_from_text


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = False
if not logger.handlers:
    handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

swimming_bot = TeleBot(token=TELEGRAM_BOT_TOKEN)


def check_tokens():
    """Проверяем наличие переменных окружения."""
    logger.info('Проверяем наличие переменных окружения')
    token_list = ['ENDPOINT', 'TELEGRAM_BOT_TOKEN']
    missing_tokens = [token for token in token_list if not globals()[token]]
    if missing_tokens:
        message_error = ('Отсутствуют переменные окружения: '
                         f'{",".join(missing_tokens)}')
        logger.critical(message_error)
        raise MissingTokens(message_error)


def load_trainings():
    """Загружает и обрабатывает список тренировок с сервера."""
    logger.info(f'Загрузка данных для тренировок с эндпоинта {ENDPOINT}...')
    try:
        trainings = requests.get(ENDPOINT).json()
        warmup = [
            task for task in trainings if task['task_type'] == 'разминка'
        ]
        main = [
            task for task in trainings if task['task_type'] not in (
                'разминка',
                'заминка'
            )
        ]
        logger.info('Данные для тренировок успешно загружены и обработаны.')
        return warmup, main
    except requests.exceptions.RequestException as e:
        logger.error(f'Не удалось загрузить тренировки: {e}')
        raise SystemExit(
            'Ошибка: не удалось получить данные для запуска бота.'
        )
    except Exception as e:
        logger.error(f'Произошла ошибка при обработке данных: {e}')
        raise SystemExit('Ошибка: неверный формат данных от API.')


@swimming_bot.message_handler(commands=['start'])
def say_hello(message):
    """Приветственное сообщение при запуске бота (кнопка /start)."""
    chat_id = message.chat.id
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_new_training = types.KeyboardButton('Хочу тренировку! 🏊🏻')
    keyboard.add(button_new_training)
    swimming_bot.send_message(
        chat_id,
        text=f'{HELLO}, {message.chat.first_name}!',
        reply_markup=keyboard
    )


def create_keyboard_for_checking_level():
    """Создаёт клавиатуру для выбора уровня подготовки."""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(
        types.KeyboardButton('Новичок'),
        types.KeyboardButton('Опытный'),
        types.KeyboardButton('Профи')
    )
    return keyboard


def create_keyboard_for_saving_file():
    """Создаёт инлайн-кнопку для сохранения в файл."""
    inline_keyboard = types.InlineKeyboardMarkup()
    save_file_btn = types.InlineKeyboardButton(
        'Сохранить в .pdf',
        callback_data='save'
    )
    inline_keyboard.add(save_file_btn)
    return inline_keyboard


def get_design_message(warmup_level, main_level):
    """Формирует сообщение с тренировкой."""
    result = []
    result.extend(warmup_level['texts'])
    result.append('----------------')
    result.extend(main_level['texts'])
    result.append('----------------')
    result.append(COOLDOWN)
    total_distance = (
        warmup_level['total_distance']
        + main_level['total_distance']
        + COOLDOWN_DISTANCE
    )
    result.append('----------------')
    result.append(f'Общая дистанция {total_distance} м')
    result_message = '\n'.join(result)
    return result_message


def send_training_for_level(chat_id, params):
    """Генерирует и отправляет тренировку для заданного уровня."""
    warmup_part = random.choice(find_combinations(
        warmup_tasks,
        params['min_warmup'],
        params['max_warmup']
    ))
    main_part = random.choice(find_combinations(
        main_tasks,
        params['min_main'],
        params['max_main']
    ))

    result_message = get_design_message(warmup_part, main_part)
    inline_keyboard = create_keyboard_for_saving_file()

    swimming_bot.send_message(
        chat_id,
        text=f'{result_message} \n',
        reply_markup=inline_keyboard
    )


@swimming_bot.message_handler(content_types=['text'])
def get_train_parameters(message):
    """
    Формирует ответ пользователю в зависимости
    от выбранного уровня подготовки.
    """
    chat_id = message.chat.id
    user_choice = message.text
    user = message.from_user

    if user_choice in LEVEL_PARAMETERS:
        logger.info(
            f'Пользователь {user.username} (ID: {user.id}) выбрал уровень '
            f'"{user_choice}". Генерируется тренировка.'
        )
        level_params = LEVEL_PARAMETERS[user_choice]
        send_training_for_level(chat_id, level_params)
    else:
        logger.info(
            f'Пользователь {user.username} '
            f'(ID: {user.id}) запросил тренировку '
            f'(текст: "{user_choice}"). '
        )
        keyboard = create_keyboard_for_checking_level()
        swimming_bot.send_message(
            chat_id,
            text='Укажите свой уровень в плавании:',
            reply_markup=keyboard
        )


@swimming_bot.callback_query_handler(func=lambda call: True)
def handle_saving_file_btn(call):
    """Обрабатывает кнопку сохранения в pdf."""
    user = call.from_user
    swimming_bot.answer_callback_query(call.id)
    if call.data == 'save':
        logger.info(
            f'Пользователь {user.username} (ID: {user.id}) нажал '
            f'кнопку "Сохранить в .pdf".'
        )
        text_for_pdf = call.message.text
        pdf_buffer = create_pdf_from_text(text_for_pdf)

        if pdf_buffer:
            swimming_bot.send_document(
                chat_id=call.message.chat.id,
                document=('swim_training.pdf', pdf_buffer.getvalue()),
                caption='Ваша тренировка в формате PDF'
            )
            logger.info(
                f'PDF для пользователя {user.username} (ID: {user.id}) '
                'успешно создан и отправлен.'
            )
        else:
            logger.warning(
                f'Не удалось создать PDF для пользователя {user.username} '
                f'(ID: {user.id}).'
            )
            swimming_bot.send_message(
                call.message.chat.id,
                'Не удалось создать PDF файл.'
            )


if __name__ == '__main__':
    check_tokens()
    warmup_tasks, main_tasks = load_trainings()
    logger.info('Бот запущен')
    swimming_bot.polling(none_stop=True)
