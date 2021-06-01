import pygame, pygame.mixer, os

def loadImage(name, colorkey = None):
    fullname = os.path.join('graphics', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        raise SystemExit(message)
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image

def loadSound(name):
    class NoneSound:
      def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
      return NoneSound()
    fullname = os.path.join('sound', name)
    try:
      sound = pygame.mixer.Sound(fullname)
    except pygame.error as message:
      raise SystemExit(message)
    return sound


