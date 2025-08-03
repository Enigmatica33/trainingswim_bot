import random
import requests
from telebot import TeleBot, types

from config import (
    TELEGRAM_BOT_TOKEN,
    ENDPOINT
)

from constants import (COOLDOWN, HELLO, MIN_WARMUP_BEGINNER, MAX_WARMUP_BEGINNER,
                       MIN_MAIN_BEGINNER, MAX_MAIN_BEGINNER, MIN_WARMUP_SKILLED,
                       MAX_WARMUP_SKILLED, MIN_MAIN_SKILLED, MAX_MAIN_SKILLED)

from logic import find_combinations

swimming_bot = TeleBot(token=TELEGRAM_BOT_TOKEN)

trainings = requests.get(ENDPOINT).json()
warmup_tasks = [task for task in trainings if task['task_type'] == 'разминка']
main_tasks = [task for task in trainings if task['task_type'] != 'разминка' and task['task_type'] != 'заминка']


@swimming_bot.message_handler(commands=['start'])
def say_hello(message):
    chat_id = message.chat.id
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_new_training = types.KeyboardButton('Хочу тренировку! 🏊🏻')
    keyboard.add(button_new_training)
    swimming_bot.send_message(
        chat_id,
        text=f'{HELLO}, {message.chat.first_name}!',
        reply_markup=keyboard
    )


@swimming_bot.message_handler(content_types=['text'])
def get_train_parameters(message):
    chat_id = message.chat.id
    result = []
    result_message = ''

    if message.text == 'Хочу тренировку! 🏊🏻':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.row(
            types.KeyboardButton('Новичок'),
            types.KeyboardButton('Опытный'),
            types.KeyboardButton('Профи')
        )
        swimming_bot.send_message(
            chat_id,
            text='Укажите свой уровень в плавании:',
            reply_markup=keyboard)

    elif message.text == 'Новичок':
        warmup_for_new = random.choice(find_combinations(warmup_tasks, MIN_WARMUP_BEGINNER, MAX_WARMUP_BEGINNER))
        main_for_new = random.choice(find_combinations(main_tasks, MIN_MAIN_BEGINNER, MAX_MAIN_BEGINNER))
        result.extend(warmup_for_new)
        result.append('----------------')
        result.extend(main_for_new)
        result.append('----------------')
        result.append(COOLDOWN)
        result_message = '\n'.join(result)
        swimming_bot.send_message(chat_id, text=f'{result_message} \n')

    elif message.text == 'Опытный':
        warmup_for_skilled = random.choice(find_combinations(warmup_tasks, MIN_WARMUP_SKILLED, MAX_WARMUP_SKILLED))
        main_for_skilled = random.choice(find_combinations(main_tasks, MIN_MAIN_SKILLED, MAX_MAIN_SKILLED))
        result.extend(warmup_for_skilled)
        result.append('----------------')
        result.extend(main_for_skilled)
        result.append('----------------')
        result.append(COOLDOWN)
        result_message = '\n'.join(result)
        swimming_bot.send_message(chat_id, text=f'{result_message} \n')


swimming_bot.polling(60)


