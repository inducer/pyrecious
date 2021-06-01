import pygame, pygame.mixer, os, random, glob

EVENT_MUSIC_END = pygame.constants.USEREVENT

MUSIC_TUNES_LIST = glob.glob("music/*.xm") + glob.glob("music/*.it")
MUSIC_TUNES_INDEX = None
MUSIC_ENABLED = 0


# Music handling --------------------------------------------------------------
def nextMusicTune():
    if not MUSIC_ENABLED:
        return

    global MUSIC_TUNES_LIST, MUSIC_TUNES_INDEX

    MUSIC_TUNES_INDEX = random.randint(0, len(MUSIC_TUNES_LIST) - 1)

    song_name = MUSIC_TUNES_LIST[MUSIC_TUNES_INDEX]

    pygame.mixer.music.load(song_name)
    pygame.mixer.music.play()


def setMusicEnabled(enabled):
    global MUSIC_ENABLED

    if MUSIC_ENABLED == enabled:
        return

    MUSIC_ENABLED = enabled

    if enabled:
        nextMusicTune()
    else:
        pygame.mixer.music.fadeout(100)
