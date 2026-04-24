import logging
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Tuple

logger = logging.getLogger(__name__)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('tetris_logs.log', encoding='utf-8'),  # Запись в файл
        logging.StreamHandler()  # Вывод в консоль
    ]
)

GAME_TITLE = "TETRIS"
VERSION_TEXT = "Version 2.0 - Material Design"

SCORES_FILENAME = "tetris_highscore.txt"

GAME_TEXT = "Tetris"
PLAY_AGAIN_TEXT = "PLAY AGAIN"
PAUSED_TEXT = "PAUSED"
RESUME_TEXT = "Press P to resume"
BEST_SCORE_TEXT = "BEST SCORE"
SCORE_TEXT = "SCORE"
LEVEL_TEXT = "LEVEL"
CONTROLS_TEXT = "CONTROLS"
NEXT_TEXT = "NEXT"
START_GAME_TEXT = "START GAME"
GAME_OVER_TEXT = "GAME OVER"

# Константы
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3

class GameCommand(Enum):
    """Команды игры"""
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    MOVE_DOWN = auto()
    ROTATE = auto()
    HARD_DROP = auto()
    START = auto()
    PAUSE = auto()
    QUIT = auto()

# Фигуры Тетриса
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 0, 0], [1, 1, 1]],  # L
    [[0, 0, 1], [1, 1, 1]],  # J
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]]  # Z
]

HINTS = [
    "← →  Move",
    "↑    Rotate",
    "↓    Drop",
    "SPACE Hard Drop"
]

CONTROLS = [
    "← →   - Move",
    "↑     - Rotate",
    "↓     - Soft Drop",
    "SPACE - Hard Drop",
    "P     - Pause",
    "ESC   - Menu"
]

# Цвета в стиле Material Design
class MaterialColors:
    """Цвета Material Design"""
    # Фигуры
    CYAN_500 = (0, 188, 212)
    AMBER_500 = (255, 193, 7)
    DEEP_PURPLE_500 = (156, 39, 176)
    DEEP_ORANGE_500 = (255, 87, 34)
    BLUE_500 = (33, 150, 243)
    GREEN_500 = (76, 175, 80)
    RED_500 = (244, 67, 54)
    
    # Интерфейс
    DARK_BG = (18, 18, 18)
    SURFACE = (30, 30, 30)
    SURFACE_LIGHT = (45, 45, 45)
    PRIMARY = (98, 0, 238)
    PRIMARY_DARK = (83, 0, 202)
    ACCENT = (0, 230, 118)
    ACCENT_DARK = (0, 200, 100)
    TEXT_PRIMARY = (255, 255, 255)
    TEXT_SECONDARY = (158, 158, 158)
    TEXT_DISABLED = (97, 97, 97)
    ERROR = (244, 67, 54)
    SUCCESS = (76, 175, 80)
    WARNING = (255, 152, 0)
    
    @classmethod
    def get_piece_colors(cls) -> List[Tuple[int, int, int]]:
        """Возвращает список цветов для фигур"""
        return [
            cls.CYAN_500,
            cls.AMBER_500,
            cls.DEEP_PURPLE_500,
            cls.DEEP_ORANGE_500,
            cls.BLUE_500,
            cls.GREEN_500,
            cls.RED_500
        ]

SHAPES_COLORS = MaterialColors.get_piece_colors()

@dataclass(frozen=True)
class GameConfig:
    """Конфигурация игры"""
    WIDTH: int = 10
    HEIGHT: int = 20
    BLOCK_SIZE: int = 30
    INITIAL_FALL_SPEED: int = 1000
    MIN_FALL_SPEED: int = 100
    SPEED_INCREMENT: int = 50
    LINES_PER_LEVEL: int = 10
    FPS: int = 60
    
    @property
    def screen_width(self) -> int:
        return self.WIDTH * self.BLOCK_SIZE + 220
    
    @property
    def screen_height(self) -> int:
        return self.HEIGHT * self.BLOCK_SIZE