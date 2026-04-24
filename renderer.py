import random
import pygame
from typing import Dict

from constants import *
from game import TetrisGame

class TetrisRenderer:

    """Отрисовка графики"""
    def __init__(self, config: GameConfig, game: TetrisGame):
        self.config = config
        self.game = game
        self.screen = pygame.display.set_mode((config.screen_width, config.screen_height))
        pygame.display.set_caption(GAME_TEXT)
        
        # Инициализация шрифтов
        self.fonts = self._init_fonts()
        
        # Кэш для поверхностей (оптимизация)
        self._surface_cache = {}
        
        # Анимация очистки линий
        self.animation_timer = 0
        self.lines_to_animate = []
        
        # Эффекты частиц
        self.particles = []
        
    # def _init_fonts(self) -> Dict[str, pygame.font.Font]:
    #     """Инициализация шрифтов"""
    #     return {
    #         'large': pygame.font.Font(None, 48),
    #         'medium': pygame.font.Font(None, 36),
    #         'small': pygame.font.Font(None, 24),
    #         'tiny': pygame.font.Font(None, 18)
    #     }

    def _init_fonts(self) -> Dict[str, pygame.font.Font]:
        """Инициализация шрифтов с поддержкой Unicode"""
        fonts = {}
        
        # Список шрифтов, поддерживающих Unicode стрелки
        unicode_fonts = [
            "Segoe UI Symbol",      # Windows
            "Arial Unicode MS",     # Windows/Mac
            "DejaVu Sans",          # Linux
            "Noto Sans",            # Linux/Android
            "Apple Color Emoji",    # Mac
            "FreeSans"              # FreeBSD/Linux
        ]
        
        # Пробуем загрузить шрифт с поддержкой Unicode
        font_loaded = False
        for font_name in unicode_fonts:
            try:
                fonts['tiny'] = pygame.font.SysFont(font_name, 18)
                # Проверяем, отображаются ли стрелки
                test_surface = fonts['tiny'].render("←", True, (255, 255, 255))
                if test_surface.get_width() > 0:
                    font_loaded = True
                    break
            except:
                continue
        
        # Если не нашли подходящий шрифт, используем стандартный
        if not font_loaded:
            fonts['tiny'] = pygame.font.Font(None, 18)
        
        # Остальные шрифты
        fonts['large'] = pygame.font.Font(None, 48)
        fonts['medium'] = pygame.font.Font(None, 36)
        fonts['small'] = pygame.font.Font(None, 24)
        
        return fonts    
    
    def _get_surface(self, key: str, size: Tuple[int, int], color: Tuple[int, int, int]) -> pygame.Surface:
        """Получение поверхности из кэша"""
        cache_key = f"{key}_{size}_{color}"
        if cache_key not in self._surface_cache:
            surface = pygame.Surface(size)
            surface.fill(color)
            self._surface_cache[cache_key] = surface
        return self._surface_cache[cache_key]
    
    def draw(self) -> None:
        """Главный метод отрисовки"""
        if self.game.game_state == GameState.PLAYING:
            self._draw_game()
            self._draw_game_ui()
            if self.game.is_paused:
                self._draw_pause_overlay()
        elif self.game.game_state == GameState.MENU:
            self._draw_game()  # Для фона
            self._draw_menu()
        elif self.game.game_state == GameState.GAME_OVER:
            self._draw_game()
            self._draw_game_ui()
            self._draw_game_over()
        
        self._draw_particles()  # Эффекты частиц
        pygame.display.flip()
    
    def _draw_game(self) -> None:
        """Отрисовка игрового поля"""
        self.screen.fill(MaterialColors.DARK_BG)
        
        # Отрисовка сетки
        for y in range(self.config.HEIGHT):
            for x in range(self.config.WIDTH):
                rect = pygame.Rect(
                    x * self.config.BLOCK_SIZE,
                    y * self.config.BLOCK_SIZE,
                    self.config.BLOCK_SIZE,
                    self.config.BLOCK_SIZE
                )
                
                if self.game.board.grid[y][x]:
                    # Отрисовка блока с эффектом градиента
                    color = self.game.board.grid[y][x]
                    pygame.draw.rect(self.screen, color, rect)
                    
                    # Эффект освещения сверху
                    highlight = pygame.Rect(rect.x, rect.y, rect.width, 3)
                    lighter_color = (
                        min(color[0] + 50, 255),
                        min(color[1] + 50, 255),
                        min(color[2] + 50, 255)
                    )
                    pygame.draw.rect(self.screen, lighter_color, highlight)
                    
                    # Тень снизу
                    shadow = pygame.Rect(rect.x, rect.y + rect.height - 3, rect.width, 3)
                    darker_color = (
                        max(color[0] - 50, 0),
                        max(color[1] - 50, 0),
                        max(color[2] - 50, 0)
                    )
                    pygame.draw.rect(self.screen, darker_color, shadow)
                    
                    pygame.draw.rect(self.screen, MaterialColors.TEXT_PRIMARY, rect, 1)
                else:
                    # Пустые клетки
                    pygame.draw.rect(self.screen, MaterialColors.SURFACE, rect)
                    pygame.draw.rect(self.screen, (40, 40, 40), rect, 1)
        
        # Отрисовка текущей фигуры
        if self.game.current_piece:
            piece = self.game.current_piece
            for y, row in enumerate(piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        rect = pygame.Rect(
                            (piece.x + x) * self.config.BLOCK_SIZE,
                            (piece.y + y) * self.config.BLOCK_SIZE,
                            self.config.BLOCK_SIZE,
                            self.config.BLOCK_SIZE
                        )
                        pygame.draw.rect(self.screen, piece.color, rect)
                        
                        # Эффект свечения
                        pygame.draw.rect(self.screen, MaterialColors.TEXT_PRIMARY, rect, 2)
                        
                        # Блик
                        highlight = pygame.Rect(rect.x, rect.y, rect.width, 3)
                        lighter_color = (
                            min(piece.color[0] + 80, 255),
                            min(piece.color[1] + 80, 255),
                            min(piece.color[2] + 80, 255)
                        )
                        pygame.draw.rect(self.screen, lighter_color, highlight)
        
        # Отрисовка сетки поверх всего
        self._draw_grid_overlay()
    
    def _draw_grid_overlay(self) -> None:
        """Отрисовка сетки сверху"""
        for y in range(self.config.HEIGHT + 1):
            pygame.draw.line(
                self.screen,
                (60, 60, 60),
                (0, y * self.config.BLOCK_SIZE),
                (self.config.WIDTH * self.config.BLOCK_SIZE, y * self.config.BLOCK_SIZE),
                1
            )
        
        for x in range(self.config.WIDTH + 1):
            pygame.draw.line(
                self.screen,
                (60, 60, 60),
                (x * self.config.BLOCK_SIZE, 0),
                (x * self.config.BLOCK_SIZE, self.config.HEIGHT * self.config.BLOCK_SIZE),
                1
            )
    
    def _draw_game_ui(self) -> None:
        """Отрисовка интерфейса"""
        right_x = self.config.WIDTH * self.config.BLOCK_SIZE
        
        # Следующая фигура
        self._draw_next_piece_card(right_x + 20)
        
        # Счет
        self._draw_score_card(right_x + 20, 260)
        
        # Управление (подсказка)
        self._draw_controls_hint(right_x + 20, self.config.screen_height - 120)
    
    def _draw_next_piece_card(self, x: int) -> None:
        """Отрисовка карточки следующей фигуры"""
        card_rect = pygame.Rect(x - 10, 100, 180, 160)
        
        # Тень
        shadow_rect = card_rect.inflate(4, 4)
        pygame.draw.rect(self.screen, MaterialColors.SURFACE, shadow_rect, border_radius=8)
        
        # Основная карточка
        pygame.draw.rect(self.screen, MaterialColors.SURFACE, card_rect, border_radius=8)
        pygame.draw.rect(self.screen, MaterialColors.PRIMARY, card_rect, 2, border_radius=8)
        
        # Заголовок
        title = self.fonts['medium'].render(NEXT_TEXT, True, MaterialColors.ACCENT)
        title_rect = title.get_rect(center=(x + 80, 125))
        self.screen.blit(title, title_rect)
        
        # Отрисовка следующей фигуры
        if self.game.next_piece:
            piece = self.game.next_piece
            piece_width = piece.width * self.config.BLOCK_SIZE
            piece_height = piece.height * self.config.BLOCK_SIZE
            offset_x = x + (160 - piece_width) // 2
            offset_y = 145 + (100 - piece_height) // 2
            
            for y, row in enumerate(piece.shape):
                for x_cell, cell in enumerate(row):
                    if cell:
                        rect = pygame.Rect(
                            offset_x + x_cell * self.config.BLOCK_SIZE,
                            offset_y + y * self.config.BLOCK_SIZE,
                            self.config.BLOCK_SIZE - 2,
                            self.config.BLOCK_SIZE - 2
                        )
                        pygame.draw.rect(self.screen, piece.color, rect, border_radius=4)
                        pygame.draw.rect(self.screen, MaterialColors.TEXT_PRIMARY, rect, 1)
    
    def _draw_score_card(self, x: int, y: int) -> None:
        """Отрисовка карточки со счетом"""
        card_rect = pygame.Rect(x - 10, y, 180, 180)
        
        # Тень
        shadow_rect = card_rect.inflate(4, 4)
        pygame.draw.rect(self.screen, MaterialColors.SURFACE, shadow_rect, border_radius=8)
        
        # Основная карточка
        pygame.draw.rect(self.screen, MaterialColors.SURFACE, card_rect, border_radius=8)
        pygame.draw.rect(self.screen, MaterialColors.PRIMARY, card_rect, 2, border_radius=8)
        
        # Score
        score_label = self.fonts['small'].render(SCORE_TEXT, True, MaterialColors.TEXT_SECONDARY)
        score_label_rect = score_label.get_rect(center=(x + 80, y + 30))
        self.screen.blit(score_label, score_label_rect)
        
        score_value = self.fonts['large'].render(str(self.game.score), True, MaterialColors.ACCENT)
        score_rect = score_value.get_rect(center=(x + 80, y + 70))
        self.screen.blit(score_value, score_rect)
        
        # Level
        level_label = self.fonts['small'].render(LEVEL_TEXT, True, MaterialColors.TEXT_SECONDARY)
        level_label_rect = level_label.get_rect(center=(x + 80, y + 115))
        self.screen.blit(level_label, level_label_rect)
        
        level_value = self.fonts['medium'].render(str(self.game.level), True, MaterialColors.TEXT_PRIMARY)
        level_rect = level_value.get_rect(center=(x + 80, y + 145))
        self.screen.blit(level_value, level_rect)
    
    def _draw_controls_hint(self, x: int, y: int) -> None:
        """Отрисовка подсказки управления"""

        
        card_rect = pygame.Rect(x - 10, y, 180, 110)
        pygame.draw.rect(self.screen, MaterialColors.SURFACE, card_rect, border_radius=8)
        pygame.draw.rect(self.screen, MaterialColors.SURFACE_LIGHT, card_rect, 1, border_radius=8)
        
        for i, hint in enumerate(HINTS):
            text = self.fonts['tiny'].render(hint, True, MaterialColors.TEXT_SECONDARY)
            self.screen.blit(text, (x, y + 10 + i * 20))
    
    def _draw_menu(self) -> None:
        """Отрисовка меню"""
        # Затемнение
        overlay = pygame.Surface((self.config.screen_width, self.config.screen_height))
        overlay.set_alpha(220)
        overlay.fill(MaterialColors.DARK_BG)
        self.screen.blit(overlay, (0, 0))
        
        # Центральная карточка
        card_width = 400
        card_height = 450
        card_x = (self.config.screen_width - card_width) // 2
        card_y = (self.config.screen_height - card_height) // 2
        
        # Анимация пульсации для карточки
        pulse = abs(pygame.time.get_ticks() % 2000 - 1000) / 1000
        border_width = int(2 + pulse)
        
        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
        pygame.draw.rect(self.screen, MaterialColors.SURFACE, card_rect, border_radius=16)
        pygame.draw.rect(self.screen, MaterialColors.PRIMARY, card_rect, border_width, border_radius=16)
        
        # Заголовок с эффектом свечения
        title = self.fonts['large'].render("TETRIS", True, MaterialColors.ACCENT)
        title_rect = title.get_rect(center=(self.config.screen_width // 2, card_y + 60))
        
        # Эффект свечения для заголовка
        for offset in range(3):
            glow_title = self.fonts['large'].render(GAME_TITLE, True, MaterialColors.PRIMARY)
            glow_rect = glow_title.get_rect(center=(self.config.screen_width // 2, card_y + 60 + offset))
            self.screen.blit(glow_title, glow_rect)
        
        self.screen.blit(title, title_rect)
        
        # Кнопка старта
        start_btn = pygame.Rect(
            (self.config.screen_width - 200) // 2,
            card_y + 140,
            200, 50
        )
        
        # Анимация кнопки
        mouse_pos = pygame.mouse.get_pos()
        if start_btn.collidepoint(mouse_pos):
            btn_color = MaterialColors.ACCENT
            pygame.draw.rect(self.screen, btn_color, start_btn, border_radius=25)
            text_color = MaterialColors.DARK_BG
        else:
            btn_color = MaterialColors.PRIMARY
            pygame.draw.rect(self.screen, btn_color, start_btn, border_radius=25)
            text_color = MaterialColors.TEXT_PRIMARY
        
        start_text = self.fonts['medium'].render(START_GAME_TEXT, True, text_color)
        start_rect = start_text.get_rect(center=start_btn.center)
        self.screen.blit(start_text, start_rect)
        
        # Лучший счет
        self._draw_high_score(card_x, card_y + 210, card_width)
        
        # Управление
        self._draw_menu_controls(card_x, card_y + 270, card_width)
        
        # Версия
        version_text = self.fonts['tiny'].render(VERSION_TEXT, True, MaterialColors.TEXT_DISABLED)
        version_rect = version_text.get_rect(center=(self.config.screen_width // 2, card_y + card_height - 20))
        self.screen.blit(version_text, version_rect)
    
    def _draw_high_score(self, x: int, y: int, width: int) -> None:
        """Отрисовка лучшего счета"""
        high_score = self._load_high_score()
        
        high_score_text = self.fonts['small'].render(BEST_SCORE_TEXT, True, MaterialColors.TEXT_SECONDARY)
        high_score_rect = high_score_text.get_rect(center=(x + width // 2, y))
        self.screen.blit(high_score_text, high_score_rect)
        
        high_score_value = self.fonts['medium'].render(str(high_score), True, MaterialColors.WARNING)
        high_score_rect = high_score_value.get_rect(center=(x + width // 2, y + 30))
        self.screen.blit(high_score_value, high_score_rect)
    
    def _load_high_score(self) -> int:
        """Загрузка лучшего счета"""
        try:
            with open(SCORES_FILENAME, "r") as f:
                return int(f.read())
        except:
            return 0
    
    def _save_high_score(self) -> None:
        """Сохранение лучшего счета"""
        try:
            with open(SCORES_FILENAME, "w") as f:
                f.write(str(self.game.score))
        except:
            pass
    
    def _draw_menu_controls(self, x: int, y: int, width: int) -> None:
        """Отрисовка управления в меню"""
        controls_title = self.fonts['small'].render(CONTROLS_TEXT, True, MaterialColors.ACCENT)
        controls_rect = controls_title.get_rect(center=(x + width // 2, y))
        self.screen.blit(controls_title, controls_rect)
                
        for i, control in enumerate(CONTROLS):
            text = self.fonts['tiny'].render(control, True, MaterialColors.TEXT_SECONDARY)
            text_rect = text.get_rect(center=(x + width // 2, y + 30 + i * 20))
            self.screen.blit(text, text_rect)
    
    def _draw_game_over(self) -> None:
        """Отрисовка экрана game over"""
        # Затемнение
        overlay = pygame.Surface((self.config.screen_width, self.config.screen_height))
        overlay.set_alpha(200)
        overlay.fill(MaterialColors.DARK_BG)
        self.screen.blit(overlay, (0, 0))
        
        # Карточка
        card_width = 350
        card_height = 280
        card_x = (self.config.screen_width - card_width) // 2
        card_y = (self.config.screen_height - card_height) // 2
        
        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
        pygame.draw.rect(self.screen, MaterialColors.SURFACE, card_rect, border_radius=16)
        pygame.draw.rect(self.screen, MaterialColors.ERROR, card_rect, 3, border_radius=16)
        
        # Текст GAME OVER
        game_over = self.fonts['large'].render(GAME_OVER_TEXT, True, MaterialColors.ERROR)
        game_over_rect = game_over.get_rect(center=(self.config.screen_width // 2, card_y + 60))
        self.screen.blit(game_over, game_over_rect)
        
        # Финальный счет
        final_score = self.fonts['medium'].render(f"Score: {self.game.score}", True, MaterialColors.ACCENT)
        score_rect = final_score.get_rect(center=(self.config.screen_width // 2, card_y + 120))
        self.screen.blit(final_score, score_rect)
        
        # Сохраняем рекорд
        self._save_high_score()
        
        # Кнопка рестарта
        restart_btn = pygame.Rect(
            (self.config.screen_width - 180) // 2,
            card_y + 180,
            180, 45
        )
        
        mouse_pos = pygame.mouse.get_pos()
        if restart_btn.collidepoint(mouse_pos):
            btn_color = MaterialColors.ACCENT
            text_color = MaterialColors.DARK_BG
        else:
            btn_color = MaterialColors.PRIMARY
            text_color = MaterialColors.TEXT_PRIMARY
        
        pygame.draw.rect(self.screen, btn_color, restart_btn, border_radius=22)
        restart_text = self.fonts['small'].render(PLAY_AGAIN_TEXT, True, text_color)
        restart_rect = restart_text.get_rect(center=restart_btn.center)
        self.screen.blit(restart_text, restart_rect)
    
    def _draw_pause_overlay(self) -> None:
        """Отрисовка оверлея паузы"""
        overlay = pygame.Surface((self.config.screen_width, self.config.screen_height))
        overlay.set_alpha(180)
        overlay.fill(MaterialColors.DARK_BG)
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.fonts['large'].render(PAUSED_TEXT, True, MaterialColors.ACCENT)
        pause_rect = pause_text.get_rect(center=(self.config.screen_width // 2, self.config.screen_height // 2))
        self.screen.blit(pause_text, pause_rect)
        
        resume_text = self.fonts['small'].render(RESUME_TEXT, True, MaterialColors.TEXT_SECONDARY)
        resume_rect = resume_text.get_rect(center=(self.config.screen_width // 2, self.config.screen_height // 2 + 50))
        self.screen.blit(resume_text, resume_rect)
    
    def _draw_particles(self) -> None:
        """Отрисовка частиц"""
        for particle in self.particles[:]:
            pygame.draw.circle(self.screen, particle['color'], particle['pos'], particle['size'])
            particle['life'] -= 1
            particle['pos'] = (particle['pos'][0] + particle['vel'][0], 
                              particle['pos'][1] + particle['vel'][1])
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def add_particles(self, x: int, y: int, color: Tuple[int, int, int], count: int = 10) -> None:
        """Добавление эффекта частиц"""
        for _ in range(count):
            self.particles.append({
                'pos': (x + random.randint(-10, 10), y + random.randint(-10, 10)),
                'vel': (random.uniform(-2, 2), random.uniform(-2, 2)),
                'size': random.randint(2, 4),
                'color': color,
                'life': random.randint(20, 40)
            })