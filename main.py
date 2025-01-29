from check_database import check_db
from loot.chest import InfinityChest, ArmorChest
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
        cell_x = (mouse_pos[0] - self.left) // self.cell_size
        cell_y = (mouse_pos[1] - self.top) // self.cell_size
        if 0 <= cell_x <= self.width and 0 <= cell_y <= self.height:
            if player.fight_mode and isinstance(self.board[cell_y][cell_x], (Monster,)) and self.board[cell_y][
                cell_x] in player.radar_list:
                player.get_damage(self.board[cell_y][cell_x])

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
    monsters_group = pygame.sprite.Group()
    all_monster = [Bee(board, x=6, y=6, default_damage=4)]
    monster = Dummy(board, 2, 3, hp=100, default_damage=0,
                    sheet=pygame.image.load('./sprites/monsters_sp/dummy_sp/dummy_spritesheet.png'),
                    columns=3, rows=1)
    slime = Slime(board, x=8, y=8)
    all_monster.append(monster)
    all_monster.append(slime)

    chest_sps = [
        LootChest(board, x=4, y=4, rarity=2),
        LootChest(board, x=4, y=5, rarity=3),
        ArmorChest(board, x=4, y=6, rarity=1),
        InfinityChest(board, x=2, y=2, rarity=3)
    ]
    running = True

    while running:
        all_monster = [monster for monster in all_monster if not monster.is_dead]
        if player.action_count <= 0:
            [i.attack_damage(player) for i in all_monster]
            player.action_count = player.action_const

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

            if event.type == pygame.KEYDOWN and not player.inventory.is_open and player.action_count:  # Обработка нажатия клавиш
                keys = pygame.key.get_pressed()
                player.update(keys, screen)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:  # Открытие инвентаря по нажатию клавиши 'I'
                    player.open_inventory()
        screen.fill((0, 0, 0))
        board.render(screen)

        if player.fight_mode:
            player.fight_cell(screen)

        screen.blit(player.image, player.rect)
        for chest in chest_sps:
            screen.blit(chest.image, chest.rect)

        if all_monster:
            for i in all_monster:
                i.update(screen)
            for i in all_monster:
                if not i.is_dead:
                    screen.blit(i.image, i.rect)
                    i.render_stats(screen)

        player.render_stats(screen)  # Рендерим статистику игрока
        player.inventory.draw(screen, player)

        if player.inventory.is_open:
            for slot in player.inventory.slots + player.inventory.unic_slot:
                item = slot.item
                if item is not None:
                    item.stats_update(screen)

        all_monster = [monster for monster in all_monster if not monster.is_dead]

        pygame.display.flip()

    pygame.quit()
