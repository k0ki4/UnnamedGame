import pygame

from player_logic import *


class Board:
    def __init__(self, width, height, padding=10):
        self.width = width
        self.height = height
        self.padding = padding

        # Вычисляем размер окна
        self.window_size = pygame.display.get_window_size()

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
        color = ["white", "#facecc", (255, 255, 255)]
        color_cell = ["red", "blue", "black"]
        for x in range(self.width):
            for y in range(self.height):
                if self.board[y][x] == 1:
                    pygame.draw.rect(
                        screen, color_cell[0],
                        (x * self.cell_size + self.left, y * self.cell_size + self.top,
                         self.cell_size, self.cell_size), 0
                    )

                if self.board[y][x] == 2:
                    pygame.draw.rect(
                        screen, color_cell[1],
                        (x * self.cell_size + self.left, y * self.cell_size + self.top,
                         self.cell_size, self.cell_size), 0
                    )

                if self.board[y][x] == 3:
                    pygame.draw.rect(
                        screen, color_cell[2],
                        (x * self.cell_size + self.left, y * self.cell_size + self.top,
                         self.cell_size, self.cell_size), 0
                    )

                pygame.draw.rect(
                    screen, color[0],
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


if __name__ == '__main__':
    pygame.init()
    fps = 60
    SIZE = width, height = 1000, 800
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Чёрное в белое и наоборот")
    board = Board(20, 20)
    player = Player(board)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    board.get_cell(event.pos)
            if event.type == pygame.KEYDOWN:  # Обработка нажатия клавиш
                keys = pygame.key.get_pressed()
                player.update(keys)

        screen.fill((0, 0, 0))
        screen.blit(player.image, player.rect)
        board.render(screen)

        player.render_stats(screen)  # Рендерим статистику игрока

        pygame.display.flip()

    pygame.quit()