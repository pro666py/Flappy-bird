import pygame as pg
from random import randint
from time import sleep


class Bird(pg.sprite.Sprite):
    def __init__(self, root) -> None:
        # наследуем спрайты
        super().__init__()

        self.game = root  # поле игры

        # кортеж всех картинок птички
        # в них отличается взмах крыла
        self.images = (
            pg.image.load('bird-up.png').convert_alpha(),
            pg.image.load('bird-middle.png').convert_alpha(),
            pg.image.load('bird-down.png').convert_alpha()
        )

        # текущая скорость птички (делаем копию)
        self.speed = self.game.speed

        self.current_image = 0 # номер текущей фотки
        self.image = self.images[0]  # получаем изначально 1 фотку как спрайт
        self.mask = pg.mask.from_surface(self.image)  # создаём маску

        # создаём хитбокс слева экрана по середине высоты
        self.rect = self.image.get_rect(x=50, y=self.game.screen_h // 2)

    def update(self) -> None:
        # получаем текущую картинку и запоминаем её
        # % 3 чтобы не выйти за границы кортежа
        self.current_image = (self.current_image + 1) % 3

        # получаем текущий спрайт и поворачиваем его в зависимости от скорости птицы
        self.image = pg.transform.rotate(self.images[self.current_image], -self.speed * 2)
        # прибавляем гравитацию
        self.speed += self.game.gravity
        # применяем скорость к хитбоксу
        self.rect.y += self.speed

    def jump(self) -> None:
        # при прыжке меняем скорость на обратную
        # чтобы взлететь
        self.speed = -self.game.speed


class Pipe(pg.sprite.Sprite):
    def __init__(self, root, inverted: bool, x_pos: int, y_pos: int) -> None:
        # наследуем спрайты
        super().__init__()
        self.game = root  # поле игры

        # грузим картинку
        self.image = pg.image.load('pipe.png').convert_alpha()

        # подгоняем картинку под размеры трубы
        self.image = pg.transform.scale(self.image,
                                        (self.game.pipe_w, self.game.pipe_h))

        # получаем хитбокс и ставим его на определённую точку x
        self.rect = self.image.get_rect(x=x_pos)

        if inverted:  # если нужна труба перевёрнутая
            # делаем отражение картинки по оси Y
            self.image = pg.transform.flip(self.image, False, True)
            # высчитываем позицию Y инвертированной трубы
            self.rect.y = - (self.rect.height - y_pos)
        else:  # иначе высчитываем позицию Y обычной трубы
            self.rect.y = self.game.screen_h - y_pos

        # создаём маску
        self.mask = pg.mask.from_surface(self.image)

    def update(self) -> None:
        # двигаем трубу налево
        self.rect.x -= self.game.speed


class Ground(pg.sprite.Sprite):
    def __init__(self, root, x_pos: int) -> None:
        # инициализируем Sprite
        super().__init__()
        self.game = root  # поле игры

        # грузим и растягиваем изображение
        self.image = pg.transform.scale(pg.image.load('base.png'),
                                        (self.game.ground_w, self.game.ground_h))
        # конвертируем изображение
        self.image = self.image.convert_alpha()

        # создаём маску по картинке
        self.mask = pg.mask.from_surface(self.image)

        # создаём хитбокс, который расположем в точке x_pos и по y внизу экрана
        self.rect = self.image.get_rect(x=x_pos,
                                        y=self.game.screen_h - self.game.ground_h)

    def update(self) -> None:
        self.rect.x -= self.game.speed


class Game:
    def __init__(self) -> None:
        pg.init()

        # размеры экрана
        self.screen_w = 400
        self.screen_h = 800

        # размеры труб
        self.pipe_w = 80
        self.pipe_h = 500

        self.pipe_gap = 180  # расстояние между трубами

        # размер земли
        self.ground_w = 2 * self.screen_w
        self.ground_h = 100

        self.speed = 10  # скорость птички
        self.gravity = 1  # гравитация

        # задаём окно и название
        self.screen = pg.display.set_mode((self.screen_w, self.screen_h))
        pg.display.set_caption('Flappy Bird')

        # грузим задний фон и подгоняем под размеры окна
        self.bg_image = pg.transform.scale(pg.image.load('bg.png'),
                                           (self.screen_w, self.screen_h))

        self.file = open('records.txt', 'r')
        self.best_score = self.file.read()  
        self.file.close()

        self.bg_music = pg.mixer.Sound('Flappy Bird (Gameplay Version With Music) - music by FMR Games.mp3')
        self.bg_music.set_volume(0.2)
        self.bg_music.play(-1)
        self.game_over_sound = pg.mixer.Sound('jg-032316-sfx-video-game-game-over-3.mp3')
        self.game_over_sound.set_volume(0.4)                                 

        self.clock = pg.time.Clock()  # часы для FPS
        self.points = 0  # Количество очков

        # шрифт для рендеринга
        self.font = pg.font.Font(pg.font.get_default_font(), 30)

        # создаём группу спрайтов и заполняем группу 2-мя спрайтами земли.
        self.ground_group = pg.sprite.Group()
        self.ground_group.add(Ground(self, self.ground_w))
        self.ground_group.add(Ground(self, self.ground_w * 2))

        # создаём группу спрайтов птицы и заполняем
        self.bird_group = pg.sprite.Group()
        self.bird = Bird(self)
        self.bird_group.add(self.bird)

        self.pipe_group = pg.sprite.Group()
        for i in range(2):
            pipes = self.get_random_pipes(self.screen_w * i + 800)
            self.pipe_group.add(pipes[0])
            self.pipe_group.add(pipes[1])

    def get_random_pipes(self, xpos):
        size = randint(100, 500)

        pipe = Pipe(self, False, xpos, size)
        pipe_inverted = Pipe(self, True, xpos, self.screen_h - size - self.pipe_gap)
        return pipe, pipe_inverted

    @staticmethod
    def is_off_screen(sprite) -> bool:
        return sprite.rect.right < 0

    def check_events(self) -> bool:
        # закрытие окна
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False

            # нажатие на пробел
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.bird.jump()  # здесь
        return True

    def draw(self) -> None:
        self.screen.blit(self.bg_image, (0, 0))

        if self.is_off_screen(self.ground_group.sprites()[0]):
            self.ground_group.remove(self.ground_group.sprites()[0])
            new_ground = Ground(self, self.ground_w - 20)
            self.ground_group.add(new_ground)

        # если трубы ушли за левую стенку
        if self.is_off_screen(self.pipe_group.sprites()[0]):
            # удаляем старые трубы
            self.pipe_group.remove(self.pipe_group.sprites()[0])
            self.pipe_group.remove(self.pipe_group.sprites()[0])

            # создаём новые трубы
            pipes = self.get_random_pipes(self.screen_w * 2)

            # добавляем новые трубы в группу спрайтов
            self.pipe_group.add(pipes[0])
            self.pipe_group.add(pipes[1])
            # увеличиваем количество очков
            self.points += 1

        self.ground_group.draw(self.screen)
        self.pipe_group.draw(self.screen)  # здесь
        self.bird_group.draw(self.screen)

        points_text = self.font.render(f"Points: {self.points}",
                                       True,
                                       pg.Color('black'))
        self.screen.blit(points_text, points_text.get_rect(x=20, y=20))

    def update(self) -> None:
        self.clock.tick(30)
        self.bird_group.update()
        self.ground_group.update()
        self.pipe_group.update()  # здесь
        pg.display.flip()

    def check_game_over(self):
        # если группа спрайтов птички касается группы земли
        if (pg.sprite.groupcollide(self.bird_group,
                                   self.ground_group,
                                   False,
                                   False, pg.sprite.collide_mask) or
            # или группа птички касается группы труб
                pg.sprite.groupcollide(self.bird_group,
                                       self.pipe_group,
                                       False,
                                       False, pg.sprite.collide_mask)) or self.bird_group.sprites()[0].rect.bottom > 850:

            # то создаём текст с хитбоксом по середине экрана, выводим его и ждём 3 секунды
            # потом приложение закрывается и в консоль пишется Game Over
            self.file = open('records.txt', 'w')
            if self.points > int(self.best_score):
                self.file.write(str(self.points))
                self.file.close()
            self.bg_music.stop()
            self.game_over_sound.play()
            text = self.font.render(f'Game Over! Record: {self.best_score}', True, pg.Color('red'))
            self.screen.blit(text, text.get_rect(center=(self.screen_w // 2, self.screen_h // 2)))
            pg.display.flip()
            sleep(3)
            self.file.close()
            game = Game()
            game.run()
            exit('Game Over')

    def run(self) -> None:
        while self.check_events():
            self.check_game_over() # Вызываем здесь
            self.draw()
            self.update()
        pg.quit()


if __name__ == '__main__':
    game = Game()
    game.run()