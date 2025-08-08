"""Обработка ответа от API,
выборка тренировок с учётом заданных параметров.
"""
import requests

from config import ENDPOINT

trainings = requests.get(ENDPOINT).json()


def find_combinations(tasks, min_dist, max_dist):
    """
    Находит все комбинации текстов задач, сумма дистанций которых
    находится в заданном диапазоне.

    :param tasks: Список словарей с задачами.
    :param min_dist: Минимальная суммарная дистанция.
    :param max_dist: Максимальная суммарная дистанция.
    :return: Список списков с текстами задач, удовлетворяющих условию.
    """
    results = []

    # Рекурсивная функция для поиска комбинаций
    def find_recursive(start_index, current_combo, current_distance):
        # 1. Проверяем, является ли текущая комбинация решением
        if min_dist <= current_distance <= max_dist:
            # Если да, извлекаем тексты и добавляем в общий список результатов
            texts = [task['text'] for task in current_combo]
            result_item = {
                'texts': texts,
                'total_distance': current_distance
            }
            results.append(result_item)

        # 2. Условие остановки рекурсии: если сумма уже превысила максимум
        # или мы перебрали все задачи, то дальше идти нет смысла.
        if current_distance > max_dist or start_index >= len(tasks):
            return

        # 3. Перебираем оставшиеся задачи, начиная со start_index
        for i in range(start_index, len(tasks)):
            task = tasks[i]
            # Рекурсивный вызов: "включаем" текущую задачу в комбинацию
            # и ищем дальше, начиная со следующей задачи (i + 1)
            find_recursive(
                i + 1,
                current_combo + [task], current_distance + task['distance']
            )

    # Запускаем рекурсивный поиск с самого начала
    find_recursive(0, [], 0)
    return results
