from random import randint
from typing import List, Optional, Tuple

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 30


DEFAULT_SNAKE_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)


# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption("Змейка")

# Настройка времени:
clock = pygame.time.Clock()


def handle_keys(game_object):
    """Функция для обработки нажатия клавиш пользователем"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit


# Тут опишите все классы игры.
class GameObject:
    """Интерфейс игрового объекта"""

    def __init__(self, body_color=SNAKE_COLOR, position=(0, 0)) -> None:
        self.body_color = body_color
        self.position = position

    def draw(self):
        """Метод для отрисовки игрового объекта"""
        pass


class Snake(GameObject):
    """Объект змейки"""

    def __init__(
        self,
        length: int = 1,
        positions: List[Tuple[int, int]] = [DEFAULT_SNAKE_POSITION],
        direction: Tuple[int, int] = RIGHT,
        next_direction: Optional[Tuple[int, int]] = None,
        body_color: Tuple[int, int, int] = SNAKE_COLOR,
        position: Tuple[int, int] = DEFAULT_SNAKE_POSITION,
    ) -> None:
        self.length = length
        self.positions = positions
        self.direction = direction
        self.next_direction = next_direction
        self.body_color = body_color
        self.position = position

        self._skip_body_move = False

    def reset(self) -> None:
        """Метод для перезапуска игры"""
        self.length = 1
        self.positions = [DEFAULT_SNAKE_POSITION]
        self.direction = RIGHT
        self.next_direction = None
        self.body_color = SNAKE_COLOR
        self.position = DEFAULT_SNAKE_POSITION

        self._skip_body_move = False

    def draw(self):
        """Метод для отрисовки змейки"""
        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def get_head_position(self) -> Tuple[int, int]:
        """Метод для получения позиции головы"""
        return self.position

    def add_body_elem(self) -> None:
        """Метод для добавления элемента тела змейки"""
        self.positions.insert(0, self.position)
        self._skip_body_move = True

    def move(self) -> None:
        """Метод для вычисления новых позиций блоков тела змейки"""
        if self._skip_body_move:
            self.positions[0] = (
                self.positions[0][0] + GRID_SIZE * self.direction[0],
                self.positions[0][1] + GRID_SIZE * self.direction[1],
            )
            self.position = self.positions[0]
            self._skip_body_move = False

        else:
            if len(self.positions) > 1:
                for i in range(len(self.positions) - 1, 0, -1):
                    self.positions[i] = self.positions[i - 1]

            self.positions[0] = (
                self.positions[0][0] + GRID_SIZE * self.direction[0],
                self.positions[0][1] + GRID_SIZE * self.direction[1],
            )
            self.position = self.positions[0]

    def update_direction(self):
        """Метод обновления направления после нажатия на кнопку"""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None


class Apple(GameObject):
    """Объект яблока"""

    def __init__(self) -> None:
        self.body_color = APPLE_COLOR
        self.position = (
            randint(0, GRID_WIDTH) * GRID_SIZE,
            randint(0, GRID_HEIGHT) * GRID_SIZE,
        )

    def draw(self):
        """Метод для отрисовки яблока"""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def randomize_position(self, blocked_cells) -> None:
        """Метод для установки новой позиции яблока"""
        while self.position in blocked_cells:
            self.position = (
                randint(1, GRID_WIDTH - 1) * GRID_SIZE,
                randint(1, GRID_HEIGHT - 1) * GRID_SIZE,
            )


def handle_walls_touch(game_object: GameObject) -> None:
    """Обработчик удара змейки об стену"""
    head = game_object.get_head_position()

    if head[0] < 0:
        game_object.positions[0] = (GRID_WIDTH * GRID_SIZE,
                                    game_object.positions[0][1])
    elif head[0] > SCREEN_WIDTH:
        game_object.positions[0] = (1 * GRID_SIZE, game_object.positions[0][1])

    if head[1] < 0:
        game_object.positions[0] = (
            game_object.positions[0][0],
            GRID_HEIGHT * GRID_SIZE,
        )
    elif head[1] > SCREEN_HEIGHT:
        game_object.positions[0] = (game_object.positions[0][0], 1 * GRID_SIZE)


def handle_apple_eat(apple: Apple, snake: Snake) -> None:
    """Обработка поедания яблока"""
    if snake.get_head_position() == apple.position:
        apple.randomize_position(snake.positions)
        snake.add_body_elem()


def handle_body_touch(snake: Snake) -> None:
    """Обработка удара о тело змейки"""
    head = snake.get_head_position()
    body = snake.positions[1:]

    for block in body:
        if head == block:
            snake.reset()


def main():
    """Запуск игры"""
    # Инициализация PyGame:
    pygame.init()
    # Тут нужно создать экземпляры классов.
    snake = Snake()
    apple = Apple()
    while True:
        clock.tick(SPEED)
        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw()
        apple.draw()
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        handle_walls_touch(snake)
        handle_body_touch(snake)
        handle_apple_eat(apple, snake)

        pygame.display.update()


if __name__ == "__main__":
    main()
