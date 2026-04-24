from typing import List, Optional
import pygame

from constants import GameCommand, GameState
from game import TetrisGame
from renderer import TetrisRenderer

class TetrisInput:
    """Обработка ввода"""
    
    def __init__(self, game: TetrisGame, renderer: Optional[TetrisRenderer] = None):
        self.game = game
        self.renderer = renderer
        self.key_repeat_delay = 150  # мс
        self.key_repeat_interval = 50  # мс
        self.last_key_time = {}
        self.active_keys = set()
        
        # Привязка клавиш
        self.key_bindings = {
            pygame.K_LEFT: GameCommand.MOVE_LEFT,
            pygame.K_RIGHT: GameCommand.MOVE_RIGHT,
            pygame.K_DOWN: GameCommand.MOVE_DOWN,
            pygame.K_UP: GameCommand.ROTATE,
            pygame.K_SPACE: GameCommand.HARD_DROP,
            pygame.K_RETURN: GameCommand.START,
            pygame.K_p: GameCommand.PAUSE,
            pygame.K_ESCAPE: GameCommand.PAUSE,
        }
    
    def handle_events(self) -> bool:
        """Обработка всех событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
            
            elif event.type == pygame.KEYUP:
                self._handle_keyup(event)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_click(event)
        
        # Обработка повторяющихся клавиш
        self._handle_key_repeat()
        
        return True
    
    def _handle_keydown(self, event: pygame.event.Event) -> None:
        """Обработка нажатия клавиши"""
        if event.key in self.key_bindings:
            command = self.key_bindings[event.key]
            self.game.execute_command(command)
            self.last_key_time[event.key] = pygame.time.get_ticks()
            self.active_keys.add(event.key)
    
    def _handle_keyup(self, event: pygame.event.Event) -> None:
        """Обработка отпускания клавиши"""
        if event.key in self.active_keys:
            self.active_keys.discard(event.key)
            if event.key in self.last_key_time:
                del self.last_key_time[event.key]
    
    def _handle_key_repeat(self) -> None:
        """Обработка автоповтора клавиш"""
        current_time = pygame.time.get_ticks()
        
        for key in list(self.active_keys):
            if key in self.key_bindings and key in self.last_key_time:
                last_time = self.last_key_time[key]
                
                # Задержка перед первым повтором
                if current_time - last_time > self.key_repeat_delay:
                    # Интервал повтора
                    repeat_count = (current_time - last_time - self.key_repeat_delay) // self.key_repeat_interval
                    if repeat_count > 0:
                        command = self.key_bindings[key]
                        self.game.execute_command(command)
                        # Обновляем время, чтобы не выполнять команду слишком часто
                        self.last_key_time[key] = current_time - (current_time - last_time) % self.key_repeat_interval
    
    def _handle_mouse_click(self, event: pygame.event.Event) -> None:
        """Обработка клика мыши (для мобильных устройств)"""
        pos = pygame.mouse.get_pos()
        
        # Проверка нажатия на кнопки в меню
        if self.game.game_state == GameState.MENU:
            card_width = 400
            card_height = 450
            card_x = (self.game.config.screen_width - card_width) // 2
            card_y = (self.game.config.screen_height - card_height) // 2
            
            start_btn = pygame.Rect(
                (self.game.config.screen_width - 200) // 2,
                card_y + 140,
                200, 50
            )
            
            if start_btn.collidepoint(pos):
                self.game.execute_command(GameCommand.START)
        
        elif self.game.game_state == GameState.GAME_OVER:
            card_width = 350
            card_height = 280
            card_x = (self.game.config.screen_width - card_width) // 2
            card_y = (self.game.config.screen_height - card_height) // 2
            
            restart_btn = pygame.Rect(
                (self.game.config.screen_width - 180) // 2,
                card_y + 180,
                180, 45
            )
            
            if restart_btn.collidepoint(pos):
                self.game.execute_command(GameCommand.START)
    
    def set_key_binding(self, key: int, command: GameCommand) -> None:
        """Установка пользовательской привязки клавиш"""
        # Удаляем старую привязку для этой команды
        for k, cmd in list(self.key_bindings.items()):
            if cmd == command:
                del self.key_bindings[k]
        
        # Добавляем новую привязку
        self.key_bindings[key] = command
    
    def get_key_binding(self, command: GameCommand) -> List[int]:
        """Получение клавиш для команды"""
        return [key for key, cmd in self.key_bindings.items() if cmd == command]
