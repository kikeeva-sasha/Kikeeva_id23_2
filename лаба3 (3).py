#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pygame
import random
import time
import sys

# Настройки экрана
WIDTH, HEIGHT = 800, 600
BACKGROUND_COLOR = (255, 255, 255)

# Настройка Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Симуляция птиц на столбах")

# Цвета
BIRD_COLOR = (0, 0, 255)
POLE_COLOR = (0, 255, 0)
FALLEN_POLE_COLOR = (255, 0, 0)

# Параметры столбов и птиц
POLE_SPACING = WIDTH // 6
POLE_WIDTH, POLE_HEIGHT = 20, 200
POLE_STRENGTH = 5  # Максимальное количество птиц на столбе
BIRD_SIZE = 6
BIRD_SITTING_TIME_RANGE = (3, 7)  # Время, которое птица сидит на столбе
POLE_REPAIR_TIME = 15  # Время восстановления упавшего столба

# Инициализация столбов
poles = [{
    'position': (POLE_SPACING * (i + 1), HEIGHT - POLE_HEIGHT),
    'strength': POLE_STRENGTH,
    'birds': [],
    'is_fallen': False,
    'fall_time': None
} for i in range(5)]

# Инициализация птиц
birds = []
num_initial_birds = 10  # Количество изначально появляющихся птиц

# Создание изначальных птиц
for i in range(1,num_initial_birds+1):
    new_bird = {
        'sit_out': 0,
        'name': i,
        'position': (random.randint(0, WIDTH), random.randint(0, HEIGHT // 2)),
        'sitting': False,
        'sitting_start': None,
        'sitting_time': random.randint(*BIRD_SITTING_TIME_RANGE),
        'target_pole': None
    }
    birds.append(new_bird)

last_bird_time = time.time()  # Время последнего появления птицы
bird_spawn_interval = 5  # Интервал появления птиц в секундах (по умолчанию 5 секунд)
delay = 1 #частота появления птиц
past = time.time()
# Основной игровой цикл
running = True
clock = pygame.time.Clock()
j = 11
while running:
    screen.fill(BACKGROUND_COLOR)

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if event.button == 1:  # Левый клик для добавления столба
                # Проверка, чтобы не создавать столбы слишком близко друг к другу
                can_add_pole = True
                for pole in poles:
                    pole_x, pole_y = pole['position']
                    if abs(mouse_x - pole_x) < POLE_WIDTH * 1.5:  # Увеличено расстояние для предотвращения наложения
                        can_add_pole = False
                        break

                if can_add_pole:
                    # Создание нового столба в месте клика с дефолтной прочностью
                    new_pole = {
                        'position': (mouse_x, HEIGHT - POLE_HEIGHT),
                        'strength': POLE_STRENGTH,
                        'birds': [],
                        'is_fallen': False,
                        'fall_time': None
                    }
                    poles.append(new_pole)
                    print(f"Добавлен новый столб на координатах ({mouse_x}, {mouse_y})")

                # Изменение прочности столба по клику мышки
                for pole in poles:
                    pole_x, pole_y = pole['position']
                    if abs(mouse_x - pole_x) < POLE_WIDTH // 2 and abs(mouse_y - pole_y) < POLE_HEIGHT:
                        new_strength = random.randint(1, 10)  # Например, случайная прочность от 1 до 10
                        pole['strength'] = new_strength
                        print(f"Прочность столба изменена на {new_strength}")
                        break

                # Создание новой птицы при клике
                new_bird = {
                    'sit_out': 0,
                    'name': j,
                    'position': (random.randint(0, WIDTH), random.randint(0, HEIGHT // 2)),
                    'sitting': False,
                    'sitting_start': None,
                    'sitting_time': random.randint(*BIRD_SITTING_TIME_RANGE),
                    'target_pole': None
                }
                birds.append(new_bird)
                j += 1
                print("Новая птица появилась!")
    if (time.time() - past) > delay:
        past = time.time()
        new_bird = {
            'sit_out': 0,
            'name': j,
            'position': (random.randint(0, WIDTH), random.randint(0, HEIGHT // 2)),
            'sitting': False,
            'sitting_start': None,
            'sitting_time': random.randint(*BIRD_SITTING_TIME_RANGE),
            'target_pole': None
        }
        birds.append(new_bird)
        j += 1
        print("Новая птица появилась!")
    # Обновление состояния столбов
    for pole in poles:
        if pole['is_fallen'] and time.time() - pole['fall_time'] > POLE_REPAIR_TIME:
            pole['is_fallen'] = False

    # Обновление состояния птиц
    for bird in birds:
        if bird['sitting'] == False:
            if bird['target_pole'] == None or poles[bird['target_pole']]['is_fallen']:
                available_poles = [int(i) for i in range(len(poles)) if not poles[i]['is_fallen']]
                if available_poles:
                    print(poles)
                    bird['target_pole'] = random.choice(available_poles)
                    print(bird['target_pole'])
            pole = poles[bird['target_pole']]
            target_x, target_y = pole['position']
            bird['position'] = (
                bird['position'][0] + (target_x - bird['position'][0]) * 0.02,
                bird['position'][1] + (target_y - bird['position'][1]) * 0.02
                )
            # Проверяем, достигла ли птица столба
            if (abs(bird['position'][0] - target_x) < 5) and (abs(bird['position'][1] - target_y) < 5):
                if len(pole['birds']) < pole['strength']:
                    pole['birds'].append(bird['name'])
                    bird['sitting'] = True
                    bird['sitting_start'] = time.time()
                else:
                    for i in pole['birds']:
                        for bird in birds:
                            if bird['name'] == i:
                                bird['sit_out'] = time.time() - bird['sitting_start']
                                bird['sitting_start'] = None
                                bird['sitting'] = False
                    pole['is_fallen'] = True
                    pole['fall_time'] = time.time()
                    pole['birds'].clear()
        elif bird['sitting']:
            # Если птица сидит, проверяем, прошло ли время ожидания
            if (time.time() - bird['sitting_start'] - bird['sit_out']) >= bird['sitting_time']:
                print(poles)
                bird['sitting'] = None
                print(bird)
                poles[bird['target_pole']]['birds'].remove(bird['name'])
                bird['target_pole'] = (poles[bird['target_pole']]['position'][0], 0)
        elif bird['sitting'] == None:
            target_x, target_y = bird['target_pole']
            bird['position'] = (
                bird['position'][0] + (target_x - bird['position'][0]) * 0.02,
                bird['position'][1] + (target_y - bird['position'][1]) * 0.02
            )
            if (abs(bird['position'][0] - target_x) < 5) and (abs(bird['position'][1] - target_y) < 5):
                birds.remove(bird)




    # Отрисовка столбов
    for pole in poles:
        color = FALLEN_POLE_COLOR if pole['is_fallen'] else POLE_COLOR
        pygame.draw.rect(screen, color, (pole['position'][0] - POLE_WIDTH // 2, pole['position'][1], POLE_WIDTH, POLE_HEIGHT))

    # Отрисовка птиц
    for bird in birds:
        pygame.draw.circle(screen, BIRD_COLOR, (int(bird['position'][0]), int(bird['position'][1])), BIRD_SIZE)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()

