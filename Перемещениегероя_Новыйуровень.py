import pygame, os, sys

pygame.init()
size = width, height = 500, 500
screen = pygame.display.set_mode(size)
pygame.display.flip()
clock = pygame.time.Clock()
FPS = 10


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha(screen)
    return image


# Чтение карты из файла — это стандартная операция работы с файлами. После чтения удобно дополнить карту до прямоугольника.
def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


# Экран заставки
def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


tile_width = tile_height = 50

# Изображения тайлов (клеточек) удобно хранить в словаре
tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('mar.png')


# функция создаст все элементы игрового поля и возвращает спрайт игрока.
def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile_empty('empty', x, y)
            elif level[y][x] == '#':
                Tile_wall('wall', x, y)
            elif level[y][x] == '@':
                Tile_empty('empty', x, y)
                new_player = Player(x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


class Tile_empty(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_empty_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Tile_wall(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_wall_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy
        if obj.rect.y >= height:
            obj.rect.y = 0

        if obj.rect.x > width - tile_width:
            obj.rect.x = 0

        if obj.rect.y < 0:
            obj.rect.y = height - tile_height

        if obj.rect.x <= - tile_width:
            obj.rect.x = width - tile_width

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2 - 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


# основной персонаж
player = None

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_empty_group = pygame.sprite.Group()
tiles_wall_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()

running = running_begin = True

level = load_level('field3.txt')
player, x, y = generate_level(level)

size = width, height = tile_width * (x + 1), tile_height * (y + 1)
screen = pygame.display.set_mode(size)
pygame.display.flip()

camera = Camera()
while running:
    dx, dy = player.rect.x, player.rect.y
    screen.fill((0, 0, 255))

    if running_begin:
        start_screen()
        running_begin = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        if player.rect.x >= 0:
            player.rect.x -= tile_width
    elif keys[pygame.K_RIGHT]:
        if player.rect.x <= width - tile_width:
            player.rect.x += tile_width
    elif keys[pygame.K_UP]:
        if player.rect.y >= 0:
            player.rect.y -= tile_width
    elif keys[pygame.K_DOWN]:
        if player.rect.y <= height - tile_width:
            player.rect.y += tile_width

    tiles_empty_group.update()
    tiles_empty_group.draw(screen)

    tiles_wall_group.update()
    tiles_wall_group.draw(screen)

    player_group.update()
    player_group.draw(screen)

    # изменяем ракурс камеры
    camera.update(player)

    # обновляем положение всех спрайтов
    for sprite in all_sprites:
        camera.apply(sprite)

    pygame.display.flip()
    clock.tick(FPS)
