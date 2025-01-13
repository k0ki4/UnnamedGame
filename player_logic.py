import time
import pygame


class InventorySlot:
    def __init__(self, x, y, width, height):
        self.size = self.x, self.y, self.width, self.height = (x, y, width, height)
        self.rect = pygame.Rect(x, y, width, height)  # Размер ячейки
        self.item = None  # Предмет, который находится в ячейке

        self.image_slot = pygame.image.load("sprites/inventory/slot.png").convert_alpha()
        self.image_slot = pygame.transform.scale(self.image_slot, (width, height))

    def draw(self, screen):
        # Рисуем границу ячейки
        screen.blit(self.image_slot, (self.x, self.y))
        if self.item:
            font = pygame.font.Font(None, 24)
            text = font.render(self.item, True, "WHITE")
            text_rect = text.get_rect(center=self.rect.center)
            screen.blit(text, text_rect)


class HelmetSlot(InventorySlot):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

        self.image_slot = pygame.image.load("sprites/inventory/helmet.png").convert_alpha()
        self.image_slot = pygame.transform.scale(self.image_slot, (width, height))

    def draw(self, screen):
        screen.blit(self.image_slot, (300, 200))


class ChestplateSlot(InventorySlot):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

        self.image_slot = pygame.image.load("sprites/inventory/chestplate.png").convert_alpha()
        self.image_slot = pygame.transform.scale(self.image_slot, (width, height))

    def draw(self, screen):
        screen.blit(self.image_slot, (300, 260))


class Inventory:
    def __init__(self):
        cell_width, cell_height = 57, 57
        cell_spacing = 0

        self.slots = []
        self.rows = 5  # Количество строк
        self.cols = 10  # Количество столбцов

        self.size = self.x, self.y, self.width, self.height = (100, 100, 600, 600)

        # Создаем ячейки инвентаря
        for row in range(self.rows):
            for col in range(self.cols):
                x = 115 + col * (cell_width + cell_spacing)
                y = 400 + row * (cell_height + cell_spacing)
                self.slots.append(InventorySlot(x, y, cell_width, cell_height))

        self.helmet = HelmetSlot(300, 300, cell_width, cell_height)
        self.chestplate = ChestplateSlot(300, 300, cell_width, cell_height)

        self.is_open = False  # Состояние инвентаря

        self.background_image = pygame.image.load("sprites/inventory/background.png").convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))

    def toggle(self):
        self.is_open = not self.is_open  # Переключение состояния инвентаря

    def add_item(self, item):
        for slot in self.slots:
            if slot.item is None:  # Находим пустую ячейку
                slot.item = item
                return True
        return False

    def draw(self, screen):
        if self.is_open:
            # Рисуем фон инвентаря
            screen.blit(self.background_image, (self.x, self.y))  # Отображаем фон на экране

            # Рисуем ячейки
            for slot in self.slots:
                slot.draw(screen)
            self.helmet.draw(screen)
            self.chestplate.draw(screen)


class Player(pygame.sprite.Sprite):
    def __init__(self, board, *groups, hp=10, default_damage=1, default_armor=1):
        super().__init__(*groups)
        self.board = board

        self.inventory = Inventory()

        self.lvl = 1

        self.default_damage = default_damage
        self.default_armor = default_armor
        self.equip_weapon = None
        self.armor = None
        self.damage = None
        self.hp = hp
        self.action_count = 4
        self.calc_stats()

        self.image = pygame.Surface((board.cell_size, board.cell_size))
        self.image.fill("ORANGE")
        self.rect = self.image.get_rect()  # Получаем прямоугольник для спрайта

        self.board.board[0][0] = 10
        self.rect.x, self.rect.y = 0 * board.cell_size + board.left, 0 * board.cell_size + board.top

        self.last_move_time = 0  # Время последнего движения
        self.move_delay = 0.2  # Задержка в секундах

        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 15)

    def calc_stats(self):
        if self.equip_weapon:
            pass
        else:
            self.armor = self.default_armor
            self.damage = self.default_damage

    def calc_cell(self, cell, action_step):
        x, y = cell
        # Проверяем границы
        if not (0 <= x + action_step[0] < self.board.width and 0 <= y + action_step[1] < self.board.height):
            return x, y  # Возвращаем текущее положение, если движение недопустимо
        if self.board.board[y + action_step[1]][x + action_step[0]] != 0:
            return x, y
        self.board.board[y][x] = 0
        return x + action_step[0], y + action_step[1]  # Возвращаем новое положение

    def render_stats(self, screen):
        # Рисуем зеленый прямоугольник для фона статистики
        stats_rect = pygame.Rect(800, 10, 190, 130)  # Прямоугольник для статистики
        pygame.draw.rect(screen, (0, 128, 0), stats_rect)  # Зеленый цвет

        # Отображаем текст статистики
        hp_text = self.font.render(f"HP: {self.hp}", True, (255, 255, 255))  # Белый текст
        damage_text = self.font.render(f"Урон: {self.damage}", True, (255, 255, 255))
        armor_text = self.font.render(f"Защита: {self.armor}", True, (255, 255, 255))
        actions_text = self.font.render(f"Осталось действий: {self.action_count}", True,
                                        (255, 255, 255))
        lvl_text = self.font.render(f"Уровень: {self.lvl}", True, (255, 255, 255))

        # Позиции текста
        screen.blit(hp_text, (820, 20))
        screen.blit(damage_text, (820, 40))
        screen.blit(armor_text, (820, 60))
        screen.blit(actions_text, (820, 80))
        screen.blit(lvl_text, (820, 100))

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

    def open_inventory(self):
        self.inventory.toggle()
