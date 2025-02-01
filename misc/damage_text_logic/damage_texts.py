import time

import pygame.font


class DamageText:
    def __init__(self, x, y, damage):
        self.x = x
        self.y = y
        self.text = f"-{damage}"
        self.alpha = 255
        self.start_time = time.time()
        self.duration = 2
        self.speed = 50
        self.font = pygame.font.Font('misc/font_ttf/Undertale-Battle-Font.ttf', 14)

    def update(self, dt):
        # Двигаем текст вверх
        self.y -= self.speed * dt
        # Уменьшаем прозрачность
        self.alpha = max(0, int(255 * (1 - (time.time() - self.start_time) / self.duration)))

    def draw(self, screen):
        if self.alpha > 0:
            shadow_surface = self.font.render(self.text, True, 'BLACK')
            shadow_surface.set_alpha(self.alpha)
            screen.blit(shadow_surface, (self.x + 2, self.y + 2))

            text_surface = self.font.render(self.text, True, 'RED')
            text_surface.set_alpha(self.alpha)
            screen.blit(text_surface, (self.x, self.y))