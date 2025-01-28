import pygame

from acss.acss_logic import Accessories
from armores.armor_logic import Armor
from potions.potion_logic import Potion
from weapons.weapon_logic import Weapon


class InventorySlot:
    def __init__(self, x, y, width, height):
        self.size = self.x, self.y, self.width, self.height = (x, y, width, height)
        self.rect = pygame.Rect(x, y, width, height)  # Размер ячейки
        self.item = None  # Предмет, который находится в ячейке

        self.image_slot = pygame.image.load("sprites/inventory/slot.png").convert_alpha()
        self.image_slot = pygame.transform.scale(self.image_slot, (width, height))
        self.image_slot.get_rect(topleft=(x, y))

    def draw(self, screen):
        # Рисуем границу ячейки
        screen.blit(self.image_slot, self.rect)
        if self.item:
            self.item.draw(screen, self.rect)

    def get_rect(self):
        return self.rect


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


# inventory

class Inventory:
    def __init__(self, player):
        self.cell_size = cell_width, cell_height = 57, 57
        cell_spacing = 0

        self.player = player

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
            AccessoriesItemSlot(235, 330, cell_width, cell_height)]

        self.is_open = False  # Состояние инвентаря

        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 20)

        self.background_image = pygame.image.load("sprites/inventory/background.png").convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))
        self.background_frame = pygame.image.load("sprites/gui/gui_2.png.").convert_alpha()
        self.background_frame = pygame.transform.scale(self.background_frame, (self.width, self.height))

    def toggle(self):
        self.is_open = not self.is_open  # Переключение состояния инвентаря

    def un_equip_item(self, slot):
        slot = slot
        item = slot.item
        item.is_equip = False
        item.open_stats = False
        slot.item = None
        self.add_item(item)

    def equip_item(self, slot):
        slot = slot
        item = slot.item

        if isinstance(item, Weapon):
            for search_slot in self.slots + self.unic_slot:
                if search_slot.item is None and isinstance(search_slot, EquipItemSlot):
                    if item.is_equip:
                        return
                    print('Слот найден')
                    slot.item = None
                    search_slot.item = item
                    search_slot.item.open_stats = False
                    item.equip(search_slot.get_rect())

        elif isinstance(item, Armor):
            slot_mapping = {
                1: HelmetSlot,
                2: ChestplateSlot,
                3: LeggingsSlot
            }

            for search_slot in self.unic_slot:
                if item.is_equip:
                    return

                slot_class = slot_mapping.get(item.unic)
                if slot_class and isinstance(search_slot, slot_class) and search_slot.item is None:
                    print('Слот найден')
                    slot.item = None
                    search_slot.item = item
                    search_slot.item.open_stats = False
                    item.equip(search_slot.get_rect())
        elif isinstance(item, Accessories):
            slot_mapping = {
                1: AccessoriesItemSlot,
                2: AccessoriesItemSlot,
                3: AccessoriesItemSlot
            }

            for search_slot in self.unic_slot:
                if item.is_equip:
                    return

                slot_class = slot_mapping.get(item.unic)
                if slot_class and isinstance(search_slot, slot_class) and search_slot.item is None:
                    slot.item = None
                    search_slot.item = item
                    search_slot.item.open_stats = False
                    item.equip(search_slot.get_rect())
        elif isinstance(item, Potion):
            item.use(self.player)

    def add_item(self, item):
        for slot in self.slots:
            if slot.item is None:  # Находим пустую ячейку
                slot.item = item
                item.set_rect(slot.rect)
                return True
        return False

    def draw(self, screen, player):
        if self.is_open:
            # Рисуем фон инвентаря
            screen.blit(self.background_image, (self.x, self.y))  # Отображаем фон на экране
            screen.blit(self.background_frame, (self.x, self.y))  # Отображаем фон на экране

            # Рисуем ячейки
            for slot in self.slots:
                slot.draw(screen)
            for slot in self.unic_slot:
                slot.draw(screen)

            xp = player.xp
            text_xp = self.font.render(f"XP: {xp}/10", True, (0, 255, 255))
            text_rect = pygame.Rect((120, 290, 10, 10))
            screen.blit(text_xp, text_rect)
