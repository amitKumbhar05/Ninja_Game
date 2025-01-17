import math
import pygame, random, sys

from Scripts.entities import PhysicsEntity, Player
from Scripts.utils import load_image, load_images, Animation
from Scripts.tilemap import Tilemap
from Scripts.clouds import clouds
from Scripts.particle import Particles

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Ninja Game")

        # Template for each
        self.screen = pygame.display.set_mode((640,480)) # Screen is the default screen
        self.display = pygame.Surface((320, 240)) # Display is the blit upon the screen
        self.clock = pygame.time.Clock()

        #Camera
        self.scroll = [0, 0]


        self.movement = [False, False, False, False] # 0: left, 1: right
        self.assets = {
            'decor' : load_images('tiles/decor'),
            'grass' : load_images('tiles/grass'),
            'large_decor' : load_images('tiles/large_decor'),
            'stone' : load_images('tiles/stone'),
            'player' : load_image('entities/player.png'),
            'background' : load_image('background.png'),
            'clouds' : load_images('clouds'),
            'player/idle' : Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run' : Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump' : Animation(load_images('entities/player/jump')),
            'player/slide' : Animation(load_images('entities/player/slide')),
            'player/wall_slide' : Animation(load_images('entities/player/wall_slide')),
            'particles/leaf' : Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particles/particle' : Animation(load_images('particles/particle'), img_dur=6, loop=False),
        }

        self.clouds = clouds(self.assets['clouds'], count=16)

        self.player = Player(self, (50, 50), (8, 15))

        self.tilemap = Tilemap(self, tile_size = 16)

        self.tilemap.load('map.json')

        self.leaf_spwaner = []

        for tree in self.tilemap.extract([('large_decor', 2)],keep=True):
            self.leaf_spwaner.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))

        self.particles = []

    def run(self):
        while True:
            self.display.blit(self.assets['background'],(0,0))

            self.scroll[0] += int((self.player.rect().centerx - self.display.get_width()/2 - self.scroll[0]) / 30)
            self.scroll[1] += int((self.player.rect().centery - self.display.get_height()/2 - self.scroll[1]) / 30)
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            for rect in self.leaf_spwaner:
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particles(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))

            # Cloud update and render
            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)

            # tilemap render
            self.tilemap.render(self.display, offset=render_scroll)
            
            # player update and render
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, offset=render_scroll)

            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)


            # Inputs

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_w:
                        self.player.jump()
                    if event.key == pygame.K_x:
                        self.player.dash()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0)) #blit display on screen
            pygame.display.update() #update each frame
            self.clock.tick(60)

Game().run()

