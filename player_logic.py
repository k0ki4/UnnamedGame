import time

import pygame
from main import Board


class Player(pygame.sprite.Sprite):
    def __init__(self, board: Board, *groups, hp=10, default_damage=1, default_armor=1):
        super().__init__(*groups)
        self.board = board

        self.default_damage= default_damage
        self.default_armor = default_armor
        self.weapon = None
        self.armor = None
        self.damage = None
        self.hp = hp
        self.action_count = 4
        self.calc_stats()


        self.image = pygame.Surface((board.cell_size, board.cell_size))
        self.image.fill("ORANGE")
        self.rect = self.image.get_rect()  # Получаем прямоугольник для спрайта
        self.rect.x, self.rect.y = 0 * board.cell_size + board.left, 0 * board.cell_size + board.top

        self.last_move_time = 0  # Время последнего движения
        self.move_delay = 0.5  # Задержка в секундах

        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 15)

    def calc_stats(self):
        if self.weapon:
            pass
        else:
            self.armor = self.default_armor
            self.damage = self.default_damage


    def calc_cell(self, cell, action_step):
        x, y = cell
        # Проверяем границы
        if not (0 <= x + action_step[0] < self.board.width and 0 <= y + action_step[1] < self.board.height):
            return x, y  # Возвращаем текущее положение, если движение недопустимо
        self.board.board[y][x] = 0
        return x + action_step[0], y + action_step[1]  # Возвращаем новое положение


    def render_stats(self, screen):
        # Рисуем зеленый прямоугольник для фона статистики
        stats_rect = pygame.Rect(800, 10, 190, 100)  # Прямоугольник для статистики
        pygame.draw.rect(screen, (0, 128, 0), stats_rect)  # Зеленый цвет

        # Отображаем текст статистики
        hp_text = self.font.render(f"HP: {self.hp}", True, (255, 255, 255))  # Белый текст
        damage_text = self.font.render(f"Урон: {self.damage}", True, (255, 255, 255))
        armor_text = self.font.render(f"Защита: {self.armor}", True, (255, 255, 255))
        actions_text = self.font.render(f"Осталось действий: {self.action_count}", True, (255, 255, 255))

        # Позиции текста
        screen.blit(hp_text, (820, 20))
        screen.blit(damage_text, (820, 40))
        screen.blit(armor_text, (820, 60))
        screen.blit(actions_text, (820, 80))


    def update(self, keys):
        current_time = time.time()
        if current_time - self.last_move_time >= self.move_delay:
            if keys[pygame.K_w]:
                x, y = self.calc_cell((self.rect.x // self.board.cell_size, self.rect.y // self.board.cell_size),
                                      (0, -1))
                self.board.board[y][x] = 10
                self.rect.x, self.rect.y = (x * self.board.cell_size + self.board.left,
                                            y * self.board.cell_size + self.board.top)
            if keys[pygame.K_s]:
                x, y = self.calc_cell((self.rect.x // self.board.cell_size, self.rect.y // self.board.cell_size),
                                      (0, 1))
                self.board.board[y][x] = 10
                self.rect.x, self.rect.y = (x * self.board.cell_size + self.board.left,
                                            y * self.board.cell_size + self.board.top)
            if keys[pygame.K_a]:
                x, y = self.calc_cell((self.rect.x // self.board.cell_size, self.rect.y // self.board.cell_size),
                                      (-1, 0))
                self.board.board[y][x] = 10
                self.rect.x, self.rect.y = (x * self.board.cell_size + self.board.left,
                                            y * self.board.cell_size + self.board.top)
            if keys[pygame.K_d]:
                x, y = self.calc_cell((self.rect.x // self.board.cell_size, self.rect.y // self.board.cell_size),
                                      (1, 0))
                self.board.board[y][x] = 10
                self.rect.x, self.rect.y = (x * self.board.cell_size + self.board.left,
                                            y * self.board.cell_size + self.board.top)
            self.last_move_time = current_time