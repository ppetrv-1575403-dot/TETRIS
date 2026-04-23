import pygame
import random
import sys
from enum import Enum, auto
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod

from renderer import TetrisRenderer
from tetris_input import TetrisInput
from constants import *
from game import TetrisGame

# Инициализация Pygame
pygame.init()

class TetrisApp:
    """Главное приложение"""
    
    def __init__(self):
        self.config = GameConfig()
        self.game = TetrisGame(self.config)
        self.renderer = TetrisRenderer(self.config, self.game)
        self.input_handler = TetrisInput(self.game, self.renderer)
        self.clock = pygame.time.Clock()
        self.running = True
    
    def run(self) -> None:
        """Главный цикл приложения"""
        while self.running:
            # Обработка ввода
            self.running = self.input_handler.handle_events()
            
            # Обновление логики
            self.game.update(pygame.time.get_ticks())
            
            # Отрисовка
            self.renderer.draw()
            
            # Ограничение FPS
            self.clock.tick(self.config.FPS)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    app = TetrisApp()
    app.run()