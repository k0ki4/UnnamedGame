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


class ChestplateSlot(InventorySlot):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

        self.image_slot = pygame.image.load("sprites/inventory/chestplate.png").convert_alpha()
        self.image_slot = pygame.transform.scale(self.image_slot, (width, height))


class LeggingsSlot(InventorySlot):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

        self.image_slot = pygame.image.load("sprites/inventory/leggings.png").convert_alpha()
        self.image_slot = pygame.transform.scale(self.image_slot, (width, height))


# Accs

class EquipItemSlot(InventorySlot):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

        self.image_slot = pygame.image.load("sprites/inventory/equip_slot.png").convert_alpha()
        self.image_slot = pygame.transform.scale(self.image_slot, (width, height))


class AccessoriesItemSlot(InventorySlot):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

        self.image_slot = pygame.image.load("sprites/inventory/accessories.png").convert_alpha()
        self.image_slot = pygame.transform.scale(self.image_slot, (width, height))


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

        self.unic_slot = [
            HelmetSlot(230, 120, cell_width, cell_height),
            ChestplateSlot(230, 180, cell_width, cell_height),
            LeggingsSlot(230, 240, cell_width, cell_height),
            EquipItemSlot(150, 120, cell_width, cell_height),
            EquipItemSlot(150, 180, cell_width, cell_height),
            AccessoriesItemSlot(115, 330, cell_width, cell_height),
            AccessoriesItemSlot(175, 330, cell_width, cell_height),
            AccessoriesItemSlot(235, 330, cell_width, cell_height),
        ]

        self.is_open = False  # Состояние инвентаря

        self.background_image = pygame.image.load("sprites/inventory/background.png").convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))
        self.background_frame = pygame.image.load("sprites/gui/gui_2.png.").convert_alpha()
        self.background_frame = pygame.transform.scale(self.background_frame, (self.width, self.height))

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
            screen.blit(self.background_frame, (self.x, self.y))  # Отображаем фон на экране

            # Рисуем ячейки
            for slot in self.slots:
                slot.draw(screen)
            for slot in self.unic_slot:
                slot.draw(screen)
