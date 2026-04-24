import pygame
import random
from typing import Optional

from components import TetrisBoard, TetrisPiece
from constants import *

class TetrisGame:
    """Основная логика игры"""
    
    def __init__(self, config: GameConfig):
        self.config = config
        self.board = TetrisBoard(config.WIDTH, config.HEIGHT)
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.current_piece: Optional[TetrisPiece] = None
        self.next_piece: Optional[TetrisPiece] = None
        self.game_state = GameState.MENU
        self.last_fall_time = 0
        self.is_paused = False
        
        self._init_pieces()
    
    def _init_pieces(self) -> None:
        """Инициализация фигур"""
        self._generate_next_piece()
        self._spawn_new_piece()
    
    def _generate_next_piece(self) -> None:
        """Генерация следующей фигуры"""
        piece_idx = random.randint(0, len(SHAPES) - 1)
        shape = [row[:] for row in SHAPES[piece_idx]]
        color = SHAPES_COLORS[piece_idx]
        self.next_piece = TetrisPiece(shape, color)
    
    def _spawn_new_piece(self) -> bool:
        """Создание новой фигуры. Возвращает False при game over"""
        if self.next_piece is None:
            self._generate_next_piece()
        
        self.current_piece = self.next_piece.clone()
        self.current_piece.x = self.config.WIDTH // 2 - self.current_piece.width // 2
        self.current_piece.y = 0
        
        self._generate_next_piece()
        
        if self.board.check_collision(self.current_piece):
            self.game_state = GameState.GAME_OVER
            return False
        return True
    
    def execute_command(self, command: GameCommand) -> None:
        """Выполнение команды"""
        if command == GameCommand.QUIT:
            self.game_state = GameState.MENU
            return
            
        if self.game_state == GameState.MENU:
            if command == GameCommand.START:
                self.reset_game()
            return
        
        if self.game_state == GameState.GAME_OVER:
            if command == GameCommand.START:
                self.reset_game()
            return
        
        if self.game_state == GameState.PLAYING:
            if command == GameCommand.PAUSE:
                self.is_paused = not self.is_paused
                return
            
            if self.is_paused:
                return
            
            if command == GameCommand.MOVE_LEFT:
                self._try_move(-1, 0)
            elif command == GameCommand.MOVE_RIGHT:
                self._try_move(1, 0)
            elif command == GameCommand.MOVE_DOWN:
                self._try_move(0, 1)
            elif command == GameCommand.ROTATE:
                self._try_rotate()
            elif command == GameCommand.HARD_DROP:
                self._hard_drop()
    
    def _try_move(self, dx: int, dy: int) -> bool:
        """Попытка переместить фигуру"""
        if not self.current_piece:
            return False
        
        if not self.board.check_collision(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        
        if dy > 0:  # Движение вниз невозможно - фиксируем фигуру
            self._merge_and_spawn()
        
        return False
    
    def _try_rotate(self) -> None:
        """Попытка повернуть фигуру"""
        if not self.current_piece:
            return
        
        rotated_piece = self.current_piece.rotate()
        # Коррекция при выходе за границы
        original_x = self.current_piece.x
        for offset in [0, -1, 1, -2, 2]:
            rotated_piece.x = original_x + offset
            if not self.board.check_collision(rotated_piece):
                self.current_piece = rotated_piece
                return
        
        # Если не удалось повернуть, оставляем как есть
    
    def _hard_drop(self) -> None:
        """Мгновенный сброс фигуры"""
        if not self.current_piece:
            return
        
        while not self.board.check_collision(self.current_piece, 0, 1):
            self.current_piece.y += 1
        
        self._merge_and_spawn()
    
    def _merge_and_spawn(self) -> None:
        """Фиксация фигуры и создание новой"""
        if not self.current_piece:
            return
        
        lines = self.board.merge_piece(self.current_piece)
        self._update_score(lines)
        
        if not self._spawn_new_piece():
            self.game_state = GameState.GAME_OVER
    
    def _update_score(self, lines: int) -> None:
        """Обновление счета и уровня"""
        if lines > 0:
            points = [0, 40, 100, 300, 1200]
            points_value = points[lines] if lines < len(points) else 2000
            self.score += points_value * self.level
            self.lines_cleared += lines
            self.level = 1 + self.lines_cleared // self.config.LINES_PER_LEVEL
    
    def reset_game(self) -> None:
        """Сброс игры"""
        self.board = TetrisBoard(self.config.WIDTH, self.config.HEIGHT)
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_state = GameState.PLAYING
        self.is_paused = False
        self._init_pieces()
        self.last_fall_time = pygame.time.get_ticks()
    
    def update(self, current_time: int) -> None:
        """Обновление состояния игры"""
        if self.game_state != GameState.PLAYING or self.is_paused:
            return
        
        fall_speed = max(
            self.config.MIN_FALL_SPEED,
            self.config.INITIAL_FALL_SPEED - (self.level - 1) * self.config.SPEED_INCREMENT
        )
        
        if current_time - self.last_fall_time > fall_speed:
            self.execute_command(GameCommand.MOVE_DOWN)
            self.last_fall_time = current_time