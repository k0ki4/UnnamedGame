import sqlite3

import pygame.sprite

potion_list = [
    {"name": "Зелье Здоровья", "effect": 'REGEN', "rarity": 1,
     "sprite_path": "sprites/potion_sp/regenerate.png"},
    {"name": "Зелье Здоровья++", "effect": 'REGEN', "rarity": 2,
     "sprite_path": "sprites/potion_sp/regenerate.png"},
    {"name": "Зелье Здоровья+++", "effect": 'REGEN', "rarity": 3,
     "sprite_path": "sprites/potion_sp/regenerate.png"},
]


class Potion(pygame.sprite.Sprite):
    def __init__(self, name, effect, rarity, sprite_path, *groups):
        super().__init__(*groups)
        self.name = name
        self.rarity = rarity
        self.sprite_path = sprite_path
        self.bonus = 0
        self.lvl_bonus = 0
        self.is_equip = False

        self.button_rect = pygame.Rect((325, 290, 150, 70))

        self.image = pygame.image.load(self.sprite_path)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = -100, -100

        self.open_stats = False
        self.effect = effect
        self.choose_effect()

        self.color_rarity = {
            1: 'WHITE',
            2: 'ORANGE',
            3: 'VIOLET',
        }
        pygame.mixer.init()

        self.use_potion_sound = pygame.mixer.Sound('misc/sound_effect/potion_use.wav')
        self.use_potion_sound.set_volume(0.1)

    def choose_effect(self):
        if isinstance(self.effect, str):
            if self.effect == 'REGEN':
                self.effect = EffectRegeneration(self)

    def use(self, player):
        print('Использование')
        self.use_potion_sound.play()
        self.effect.use_effect(player)
        self.end_use(player)

    def on_click(self, player):
        print(f'Выбранна броня: {self.name}' if not self.open_stats else "Выбор снят")
        for slot in player.inventory.slots + player.inventory.unic_slot:
            if slot.item is not None and slot.item != self:
                slot.item.open_stats = False
        self.open_stats = not self.open_stats

    def stats_update(self, screen):
        if self.open_stats:
            frame = pygame.image.load('./sprites/gui/gui.png').convert_alpha()
            frame = pygame.transform.scale(frame, (300, 265))
            rect_frame = frame.get_rect(topleft=(310, 120))
            frame2 = pygame.image.load('./sprites/gui/gui_2.png').convert_alpha()
            frame2 = pygame.transform.scale(frame2, (300, 265))
            rect_frame2 = frame.get_rect(topleft=(310, 120))

            pygame.font.init()
            font_medium = pygame.font.SysFont('Arial', 20)
            font_large = pygame.font.SysFont('Arial', 30)

            name = font_large.render(f"{self.name}", True, self.color_rarity[self.rarity])  # Белый текст
            protect_text = font_medium.render(f"Эффект {self.effect.name}: {self.effect.base_regen}",
                                              True,
                                              (255, 255, 255))
            button_text = font_medium.render("Использовать", True, (255, 255, 255))
            text_rect = button_text.get_rect(center=self.button_rect.center)

            frame_button = pygame.image.load('./sprites/inventory/button.png').convert_alpha()
            frame_button = pygame.transform.scale(frame_button, (150, 70))

            screen.blit(frame, rect_frame)
            screen.blit(frame2, rect_frame2)

            cord_text_x = 325
            screen.blit(name, (cord_text_x, 130))
            screen.blit(protect_text, (cord_text_x, 200))

            screen.blit(frame_button, self.button_rect)
            screen.blit(button_text, text_rect)

    def set_rect(self, rect):
        self.rect = rect

    def draw(self, screen, slot_rect):
        slot_rect = slot_rect
        self.image = pygame.transform.scale(self.image, (slot_rect[2], slot_rect[3]))
        screen.blit(self.image, slot_rect)

    def end_use(self, player):
        self.open_stats = False
        for search_slot in player.inventory.slots:
            if search_slot.item == self:
                search_slot.item = None
                print('OK')
        self.kill()
        return False

    def get_name(self):
        return self.name

    def return_copy(self):
        return Potion(self.name, self.effect, self.rarity, self.sprite_path)


class EffectRegeneration:
    def __init__(self, potion):
        self.potion = potion
        self.name = "Регенерация"
        self.base_regen = 10
        self.bonus_effect_from_rarity()

    def bonus_effect_from_rarity(self):
        self.base_regen *= self.potion.rarity

    def use_effect(self, player):
        new_hp = player.hp + self.base_regen
        if new_hp > player.max_hp:
            player.hp = player.max_hp
        else:
            player.hp = new_hp



def randomize_potion():
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT name, effect, rarity, sprite_path FROM potion")
        potion_data = cursor.fetchall()
    return [Potion(name=name, effect=effect, rarity=rarity, sprite_path=sprite_path) for
            name, effect, rarity, sprite_path in potion_data]


result_potion = randomize_potion()
