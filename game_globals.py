from tools import *
from loaders import *
from game_tools import *

COLORS = [ 'blue', 'yellow', 'green', 'pink', 'red', 'magenta', 'cyan' ]
STONE_IMAGES = { }
LIT_STONE_IMAGES = { }

SYSTEM_FONT_SMALL = tReference( None )
SYSTEM_FONT_BIG = tReference( None )

SOUND_INVALID = tReference( None )
SOUND_DROP = tReference( None )
SOUND_DESTROY = tReference( None )
SOUND_HINT = tReference( None )
SOUND_OPPONENT = tReference( None )
SOUND_EXCELLENT = tReference( None )
SOUND_GAME_OVER = tReference( None )
SOUNDMGR_DESTROY = tReference( None )
SOUNDMGR_DROP = tReference( None )

SOUND_MANAGERS = []




# Initialization --------------------------------------------------------------
def loadPictureList( basename ):
  images = [ ]
  i = 0
  try:
    while 1: 
      name = "%s-%03d.png" % ( basename, i )
      images.append( loadImage( name ) );
      i = i + 1
  except:
    pass
 
  return images 

def loadStones():
  for color in COLORS:
    STONE_IMAGES[ color ] = loadPictureList( 
	os.path.join( "gems", color ) )
    LIT_STONE_IMAGES[ color ] = loadPictureList( 
	os.path.join( "gems", color + "-lit" ) )

def loadSounds():
  SOUND_INVALID.set( loadSound( 'invalid.wav' ) )
  SOUND_DESTROY.set( loadSound( 'destroy.wav' ) )
  SOUND_DROP.set( loadSound( 'drop.wav' ) )
  SOUND_HINT.set( loadSound( 'hint.wav' ) )
  SOUND_OPPONENT.set( loadSound( 'opponent.wav' ) )
  SOUND_EXCELLENT.set( loadSound( 'excellent.wav' ) )
  SOUND_GAME_OVER.set( loadSound( 'game_over.wav' ) )

  SOUNDMGR_DESTROY.set( tOnceSoundManager( SOUND_DESTROY.get() ) )
  SOUNDMGR_DROP.set( tOnceSoundManager( SOUND_DROP.get() ) )

  SOUND_MANAGERS.append( SOUNDMGR_DESTROY.get() )
  SOUND_MANAGERS.append( SOUNDMGR_DROP.get() )

def loadFonts():
  SYSTEM_FONT_SMALL.set( pygame.font.Font( 
    os.path.join( "fonts", "verdanab.ttf" ) , 15 ) )
  SYSTEM_FONT_BIG.set( pygame.font.Font( 
    os.path.join( "fonts", "verdanab.ttf" ), 30 ) )


