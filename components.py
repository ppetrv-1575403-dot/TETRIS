from typing import List, Tuple

class TetrisPiece:
    """Управление фигурой"""
    __slots__ = ('shape', 'color', 'x', 'y')
    
    def __init__(self, shape: List[List[int]], color: Tuple[int, int, int]):
        self.shape = [row[:] for row in shape]
        self.color = color
        self.x = 0
        self.y = 0
    
    def rotate(self) -> 'TetrisPiece':
        """Возвращает новую повернутую фигуру"""
        rotated = list(zip(*self.shape[::-1]))
        return TetrisPiece([list(row) for row in rotated], self.color)
    
    def clone(self) -> 'TetrisPiece':
        """Создает копию фигуры"""
        return TetrisPiece(self.shape, self.color)
    
    @property
    def width(self) -> int:
        return len(self.shape[0])
    
    @property
    def height(self) -> int:
        return len(self.shape)

class TetrisBoard:
    """Управление игровым полем"""
    __slots__ = ('width', 'height', 'grid')
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
    
    def check_collision(self, piece: TetrisPiece, offset_x: int = 0, offset_y: int = 0) -> bool:
        """Проверка коллизии фигуры с полем"""
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    board_x = piece.x + x + offset_x
                    board_y = piece.y + y + offset_y
                    
                    if (board_x < 0 or board_x >= self.width or 
                        board_y >= self.height or 
                        (board_y >= 0 and board_y < self.height and self.grid[board_y][board_x])):
                        return True
        return False
    
    def merge_piece(self, piece: TetrisPiece) -> int:
        """Фиксирует фигуру на поле и возвращает количество очищенных линий"""
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    board_x = piece.x + x
                    board_y = piece.y + y
                    if 0 <= board_y < self.height and 0 <= board_x < self.width:
                        self.grid[board_y][board_x] = piece.color
        
        return self._clear_lines()
    
    def _clear_lines(self) -> int:
        """Очищает заполненные линии и возвращает их количество"""
        lines_cleared = 0
        y = self.height - 1
        
        while y >= 0:
            if all(self.grid[y]):
                del self.grid[y]
                self.grid.insert(0, [0 for _ in range(self.width)])
                lines_cleared += 1
            else:
                y -= 1
        
        return lines_cleared