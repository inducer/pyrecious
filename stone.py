import random

from game_globals import *
from game_tools import *

class tStone:
  def __init__(self):
    self.Type = random.randint(0, len(COLORS) - 1)
    self.Animation = tAnimation(STONE_IMAGES[ COLORS[ self.Type ] ], 0.04)
    self.Position = (0., 0.)
    self.Velocity = (0., 0.)
    self.Acceleration = (0., 0.)
    self.StopPositionX = None
    self.StopPositionY = None
    self.MoveDelay = 0
    self.Shown = 1
    self.PlaySoundAtMoveEnd = 0
    self.Shrinking = 0
    self.Size = 1
    self.LightLevel = 0

    self.Blinking = 0
    self.BlinkOn = 0
    self.BlinkTimeout = 0

  def type(self):
    return self.Type

  def render(self, surface, base_position):
    if not self.Shown:
      return

    (x, y) = self.Position
    (bx, by) = base_position
    stone_surface = self.Animation.getCurrentFrame()

    (w_orig, h_orig) = stone_surface.get_size()
    if self.Size != 1:
      (w, h) = stone_surface.get_size()
      w = int(w * self.Size)
      h = int(h * self.Size)
      stone_surface = pygame.transform.scale(stone_surface, (w, h))
    else:
      w = w_orig
      h = h_orig

    surface.blit(stone_surface, 
	(int(x + bx + (w_orig - w) / 2), 
	  int(y + by + (h_orig - h) / 2)))

  def step(self, seconds):
    self.Animation.step(seconds)

    if self.Blinking:
      self.BlinkTimeout -= seconds
      while self.BlinkTimeout < 0:
	self.BlinkTimeout += 0.5
	self.BlinkOn = 1 - self.BlinkOn
	if self.BlinkOn:
	  self.lightUp()
	else:
	  self.darken()

    if self.Shrinking:
      self.Size -= seconds * 5
      if self.Size <= 0:
	self.setShown(0)
	self.Shrinking = 0
	self.Size = 0

    if self.MoveDelay > 0:
      self.MoveDelay -= seconds

    if self.MoveDelay <= 0:
      (x, y) = self.Position
      (vx, vy) = self.Velocity
      (ax, ay) = self.Acceleration

      px = x
      py = y
      x += seconds * vx
      y += seconds * vy
      vx += seconds * ax
      vy += seconds * ay

      # did we just pass over our stop position?
      if self.StopPositionX is not None:
	sx = self.StopPositionX
	if ((px - sx) * (x - sx) < 0):
	  x = sx
	  vx = 0
	  ax = 0
	  if self.PlaySoundAtMoveEnd:
	    SOUNDMGR_DROP.get().play()
	  self.StopPositionX = None

      if self.StopPositionY is not None:
	sy = self.StopPositionY
	if ((py - sy) * (y - sy) < 0):
	  y = sy
	  vy = 0
	  ay = 0
	  if self.PlaySoundAtMoveEnd:
	    SOUNDMGR_DROP.get().play()
	  self.StopPositionY = None

        self.StopPosition = None

      self.Position = (x, y)
      self.Velocity = (vx, vy)
      self.Acceleration = (ax, ay)

  # movement control ----------------------------------------------------------
  def setPosition(self, position):
    self.Position = position

  def disableStopPosition(self):
    self.StopPositionX = None
    self.StopPositionY = None

  def setStopPosition(self, (px, py), play_sound_at_end):
    self.StopPositionX = px
    self.StopPositionY = py
    self.PlaySoundAtMoveEnd = play_sound_at_end

  def setVelocity(self, velo):
    self.Velocity = velo

  def setAcceleration(self, accel):
    self.Acceleration = accel

  def setMoveDelay(self, md):
    self.MoveDelay = md

  def isOnTheMove(self):
    (vx, vy) = self.Velocity
    (ax, ay) = self.Acceleration
    return not (vx == 0 and vy == 0 and ax == 0 and ay == 0) or self.Shrinking

  # Visual properties ---------------------------------------------------------
  def startShrinking(self):
    self.Shrinking = 1

  def needsToStayAlive(self):
    return self.Shown
  def setShown(self, shown):
    self.Shown = shown

  def animate(self):
    self.Animation.setActive(1)

  def stopAnimation(self):
    self.Animation.finish()

  def stopAnimationQuickly(self):
    self.Animation.finishQuickly()
    
  def resetAnimation(self):
    self.Animation.reset()
    self.Animation.setActive(0)
 
  def setBlinking(self, blink):
    if blink == self.Blinking:
      return

    if blink:
      self.BlinkTimeout = 0
      self.BlinkOn = 0
    else:
      if self.Blinking and self.BlinkOn:
	self.darken()
    self.Blinking = blink

  def lightUp(self):
    self.LightLevel += 1
    self.updateImageArray()

  def darken(self):
    self.LightLevel -= 1
    self.updateImageArray()

  def updateImageArray(self):
    if self.LightLevel:
      self.Animation.setImageArray(LIT_STONE_IMAGES[ COLORS[ self.Type ] ]) 
    else:
      self.Animation.setImageArray(STONE_IMAGES[ COLORS[ self.Type ] ]) 


