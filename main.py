from check_database import check_db
from loot.chest import InfinityChest
from monsters.monster_logic import *
from player_logic import *
import pygame


class Board:
    def __init__(self, width, height, padding=10):
        self.width = width
        self.height = height
        self.padding = padding

        # Вычисляем размер окна
        self.window_size = pygame.display.get_window_size()

        self.grass = pygame.image.load('sprites/grass.jpg').convert_alpha()

        # Вычисляем размер ячейки с учетом отступов
        self.cell_size = (self.window_size[0] - 2 * padding) // self.width
        if (self.cell_size * self.height + 2 * padding) > self.window_size[1]:
            self.cell_size = (self.window_size[1] - 2 * padding) // self.height

        # Инициализация доски
        self.board = [[0] * width for _ in range(height)]
        self.left = padding
        self.top = padding

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        color = ["white", "#403a3a", (255, 255, 255)]
        for x in range(self.width):
            for y in range(self.height):

                # Отображаем спрайт, если он существует
                if self.grass:
                    sprite = self.grass
                    sprite = pygame.transform.scale(sprite, (self.cell_size, self.cell_size))  # Изменяем размер спрайта
                    screen.blit(sprite, (x * self.cell_size + self.left, y * self.cell_size + self.top))

                pygame.draw.rect(
                    screen, color[1],
                    (x * self.cell_size + self.left, y * self.cell_size + self.top,
                     self.cell_size, self.cell_size), 1
                )

    def get_cell(self, mouse_pos):
        print(mouse_pos)
        cell_x = (mouse_pos[0] - self.left) // self.cell_size
        cell_y = (mouse_pos[1] - self.top) // self.cell_size
        if (0 <= cell_x <= self.width and 0 <= cell_y <= self.height):
            print(cell_x, cell_y)
            return cell_x, cell_y
        return None

    def on_click(self, cell_coords):
        print(cell_coords)

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        self.on_click(cell)

    def get_player(self):
        for x in range(self.width):
            for y in range(self.height):
                if isinstance(self.board[y][x], Player):
                    return self.board[y][x]


if __name__ == '__main__':
    check_db()
    pygame.init()
    fps = 60
    SIZE = width, height = 1200, 800
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Unnamed Game")
    board = Board(10, 10)
    player = Player(board)
    monster = Dummy(board, 3, 3, hp=100, default_damage=0)
    loot = LootChest(board, x=3, y=4, rarity=2)
    loot2 = LootChest(board, x=4, y=5, rarity=3)
    infinity_chest = InfinityChest(board, x=2, y=2, rarity=3)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not player.inventory.is_open:
                    board.get_cell(event.pos)
                elif event.button == 1 and player.inventory.is_open:
                    for slot in player.inventory.slots + player.inventory.unic_slot:
                        item = slot.item
                        if item is not None and item.rect.topleft[0] >= 0 and item.rect.topleft[1] >= 0:
                            if item.rect.collidepoint(event.pos):
                                item.on_click(player)
                            elif item.button_rect.collidepoint(event.pos) and item.open_stats and not item.is_equip:
                                player.inventory.equip_item(slot)
                            elif item.button_rect.collidepoint(event.pos) and item.open_stats and item.is_equip:
                                player.inventory.un_equip_item(slot)

            if event.type == pygame.KEYDOWN and not player.inventory.is_open:  # Обработка нажатия клавиш
                keys = pygame.key.get_pressed()
                player.update(keys)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:  # Открытие инвентаря по нажатию клавиши 'I'
                    player.open_inventory()
        screen.fill((0, 0, 0))
        board.render(screen)
        screen.blit(player.image, player.rect)
        screen.blit(monster.image, monster.rect)
        screen.blit(loot.image, loot.rect)
        screen.blit(loot2.image, loot2.rect)
        screen.blit(infinity_chest.image, infinity_chest.rect)

        player.render_stats(screen)  # Рендерим статистику игрока
        player.inventory.draw(screen)

        if player.inventory.is_open:
            for slot in player.inventory.slots + player.inventory.unic_slot:
                item = slot.item
                if item is not None:
                    item.stats_update(screen)

        pygame.display.flip()

    pygame.quit()
