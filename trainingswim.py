import random
import requests
from telebot import TeleBot, types

from config import (
    TELEGRAM_BOT_TOKEN,
    ENDPOINT
)

from constants import (COOLDOWN, COOLDOWN_DISTANCE, HELLO, MIN_WARMUP_BEGINNER,
                       MAX_WARMUP_BEGINNER, MIN_MAIN_BEGINNER,
                       MAX_MAIN_BEGINNER, MIN_WARMUP_SKILLED,
                       MAX_WARMUP_SKILLED, MIN_MAIN_SKILLED, MAX_MAIN_SKILLED,
                       MIN_WARMUP_PROFI, MAX_WARMUP_PROFI, MIN_MAIN_PROFI,
                       MAX_MAIN_PROFI)

from logic import find_combinations
from saving_pdf import create_pdf_from_text

swimming_bot = TeleBot(token=TELEGRAM_BOT_TOKEN)

trainings = requests.get(ENDPOINT).json()
warmup_tasks = [task for task in trainings if task['task_type'] == 'разминка']
main_tasks = (
    [task for task in trainings if task['task_type'] != 'разминка'
     and task['task_type'] != 'заминка']
)
user_message_text = {}


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


@swimming_bot.message_handler(content_types=['text'])
def get_train_parameters(message):
    chat_id = message.chat.id

    if message.text == 'Новичок':
        warmup_for_new = random.choice(find_combinations(
            warmup_tasks,
            MIN_WARMUP_BEGINNER,
            MAX_WARMUP_BEGINNER
        ))
        main_for_new = random.choice(find_combinations(
            main_tasks,
            MIN_MAIN_BEGINNER,
            MAX_MAIN_BEGINNER
        ))
        result_message = get_design_message(warmup_for_new, main_for_new)
        inline_keyboard = create_keyboard_for_saving_file()
        user_message_text[message.chat.id] = result_message
        swimming_bot.send_message(
            chat_id,
            text=f'{result_message} \n',
            reply_markup=inline_keyboard
        )

    elif message.text == 'Опытный':
        warmup_for_skilled = random.choice(find_combinations(
            warmup_tasks,
            MIN_WARMUP_SKILLED,
            MAX_WARMUP_SKILLED
        ))
        main_for_skilled = random.choice(find_combinations(
            main_tasks,
            MIN_MAIN_SKILLED,
            MAX_MAIN_SKILLED
        ))
        result_message = get_design_message(
            warmup_for_skilled,
            main_for_skilled
        )
        inline_keyboard = create_keyboard_for_saving_file()
        user_message_text[message.chat.id] = result_message
        swimming_bot.send_message(
            chat_id,
            text=f'{result_message} \n',
            reply_markup=inline_keyboard
        )

    elif message.text == 'Профи':
        warmup_for_profi = random.choice(find_combinations(
            warmup_tasks,
            MIN_WARMUP_PROFI,
            MAX_WARMUP_PROFI
        ))
        main_for_profi = random.choice(find_combinations(
            main_tasks,
            MIN_MAIN_PROFI,
            MAX_MAIN_PROFI
        ))
        result_message = get_design_message(
            warmup_for_profi,
            main_for_profi
        )
        inline_keyboard = create_keyboard_for_saving_file()
        user_message_text[message.chat.id] = result_message
        swimming_bot.send_message(
            chat_id,
            text=f'{result_message} \n',
            reply_markup=inline_keyboard
        )
    else:
        keyboard = create_keyboard_for_checking_level()
        swimming_bot.send_message(
            chat_id,
            text='Укажите свой уровень в плавании:',
            reply_markup=keyboard)


@swimming_bot.callback_query_handler(func=lambda call: True)
def handle_saving_file_btn(call):
    swimming_bot.answer_callback_query(call.id)
    if call.data == 'save':
        text_for_pdf = user_message_text.get(call.message.chat.id)
        pdf_buffer = create_pdf_from_text(text_for_pdf)

        if pdf_buffer:
            swimming_bot.send_document(
                chat_id=call.message.chat.id,
                document=(f'swim_training_{call.message.chat.username}.pdf', pdf_buffer)
            )


swimming_bot.polling(60)
