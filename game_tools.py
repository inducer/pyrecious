import pygame

# Functions -------------------------------------------------------------------
def getTime():
    return float(pygame.time.get_ticks()) / 1000


# Classes ---------------------------------------------------------------------
class tOnceSoundManager:
    def __init__(self, sound):
        self.Sound = sound
        self.ShouldPlay = 0

    def play(self):
        self.ShouldPlay = 1

    def step(self, seconds):
        if self.ShouldPlay:
            self.ShouldPlay = 0
            self.Sound.play()


class tAnimation:
    def __init__(self, image_array, delay):
        self.ImageArray = image_array
        self.FrameDelay = delay
        self.Time = 0
        self.FrameIndex = 0
        self.Active = 0
        self.OneShot = 0
        self.Quickly = 0

    def step(self, seconds):
        if self.Active:
            self.Time += seconds
            delay = self.FrameDelay
            if self.Quickly:
                delay /= 2
            while self.Time > delay:
                self.FrameIndex = self.FrameIndex + 1
                if self.FrameIndex >= len(self.ImageArray):
                    self.FrameIndex = 0
                    if self.OneShot:
                        self.Active = 0
                        self.Quickly = 0
                    break
                self.Time -= delay

    def getCurrentFrame(self):
        return self.ImageArray[self.FrameIndex]

    def setImageArray(self, iarray):
        self.ImageArray = iarray
        if self.FrameIndex >= len(self.ImageArray):
            self.FrameIndex = 0

    def setActive(self, active):
        self.Active = active
        self.OneShot = 0
        self.Quickly = 0

    def startOneShot(self):
        self.Active = 1
        self.OneShot = 1

    def finish(self):
        self.OneShot = 1

    def finishQuickly(self):
        self.OneShot = 1
        self.Quickly = 1

    def reset(self):
        self.FrameIndex = 0
