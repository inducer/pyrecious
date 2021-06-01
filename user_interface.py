import os, pygame, pygame.font, pygame.mixer, inspect
from pygame.locals import *

from game_globals import *


MOUSE_GRAB = None


class tColorSet:
    def __init__(self):
        self.Highlight = (255, 255, 255)
        self.SubHighlight = (220, 220, 220)
        self.SubShadow = (150, 150, 150)
        self.Shadow = (100, 100, 100)
        self.Inner = (200, 200, 200)


def draw3DBox(surface, x, y, w, h, colorset):
    # outer
    pygame.draw.line(surface, colorset.Highlight, (x, y), (x + w, y))
    pygame.draw.line(surface, colorset.Highlight, (x, y), (x, y + h))
    pygame.draw.line(surface, colorset.Shadow, (x + w, y), (x + w, y + h))
    pygame.draw.line(surface, colorset.Shadow, (x, y + h), (x + w, y + h))

    # inner
    pygame.draw.line(surface, colorset.SubHighlight, (x + 1, y + 1), (x + w - 1, y + 1))
    pygame.draw.line(surface, colorset.SubHighlight, (x + 1, y + 1), (x + 1, y + h - 1))
    pygame.draw.line(
        surface, colorset.SubShadow, (x + w - 1, y + 1), (x + w - 1, y + h - 1)
    )
    pygame.draw.line(
        surface, colorset.SubShadow, (x + 1, y + h - 1), (x + w - 1, y + h - 1)
    )

    pygame.draw.rect(surface, colorset.Inner, pygame.Rect((x + 2, y + 2, w - 3, h - 3)))


class tDialogBox:
    def __init__(self, position, width, height):
        self.Position = position
        self.Width = width
        self.Height = height

    def render(self, surface):
        (x, y) = self.Position
        w = self.Width
        h = self.Height

        colorset = tColorSet()

        draw3DBox(surface, x, y, w, h, colorset)


class tButtonBase:
    def __init__(self, position, width, height, text, initial_state):
        self.Position = position
        self.Width = width
        self.Height = height
        self.Text = text
        self.Pushed = 0
        self.Activated = 0
        self.State = initial_state

    def render(self, surface):
        (x, y) = self.Position
        w = self.Width
        h = self.Height

        colorset = tColorSet()
        if self.Pushed or self.State:
            colorset.Shadow = (255, 255, 255)
            colorset.SubShadow = (220, 220, 220)
            colorset.SubHighlight = (150, 150, 150)
            colorset.Highlight = (100, 100, 100)
            if self.Pushed:
                colorset.Inner = (180, 180, 180)
            else:
                colorset.Inner = (200, 200, 200)

        draw3DBox(surface, x, y, w, h, colorset)

        (tw, th) = SYSTEM_FONT_SMALL.get().size(self.Text)
        text_surf = SYSTEM_FONT_SMALL.get().render(self.Text, 1, (0, 0, 0, 0))
        if self.Pushed:
            x += 1
            y += 1
        surface.blit(text_surf, (x + (w - tw) / 2, y + (h - th) / 2))

    def buttonDown(self, position, button):
        global MOUSE_GRAB

        if button != 1:
            return 0

        (x, y) = self.Position
        (mx, my) = position
        if x <= mx <= x + self.Width and y <= my <= y + self.Height:
            MOUSE_GRAB = self
            self.Pushed = 1
            self.Activated = 1

    def buttonUp(self, position, button):
        global MOUSE_GRAB

        if button != 1:
            return 0

        if not self.Activated:
            return 0

        self.Pushed = 0
        self.Activated = 0
        MOUSE_GRAB = None

        (x, y) = self.Position
        (mx, my) = position
        if x <= mx <= x + self.Width and y <= my <= y + self.Height:
            self.clicked()

    def mouseMove(self, position):
        (x, y) = self.Position
        (mx, my) = position
        self.Pushed = (
            self.Activated and x <= mx <= x + self.Width and y <= my <= y + self.Height
        )

    def clicked(self):
        pass

    def setText(self, text):
        self.Text = text


class tButton(tButtonBase):
    def __init__(self, position, width, height, text, action):
        tButtonBase.__init__(self, position, width, height, text, 0)
        self.Action = action

    def clicked(self):
        self.Action()


class tToggleButton(tButtonBase):
    def __init__(self, position, width, height, text, initial_state, toggle_action):
        tButtonBase.__init__(self, position, width, height, text, initial_state)
        self.Action = toggle_action

    def clicked(self):
        self.State = not self.State
        self.Action(self.State)


class tLabel:
    def __init__(self, position, text):
        self.Position = position
        self.Text = text

    def render(self, surface):
        if self.Text != "":
            text_surf = SYSTEM_FONT_SMALL.get().render(self.Text, 1, (0, 0, 0, 0))
            surface.blit(text_surf, self.Position)

    def setText(self, text):
        self.Text = text


class tFloatUpAndFadeLabel:
    def __init__(self, position):
        self.StartPosition = position
        self.Position = self.StartPosition
        self.Opacity = 0.0

    def step(self, seconds):
        if self.Opacity > 0:
            self.Opacity -= seconds * 1
            if self.Opacity < 0:
                self.Opacity = 0
            (x, y) = self.Position
            self.Position = (x, y - 50 * seconds)

    def render(self, surface):
        if self.Opacity == 0:
            return

        scaled_opacity = 200 - int(200 * self.Opacity)
        text_surf = SYSTEM_FONT_SMALL.get().render(
            self.Text, 1, (scaled_opacity, scaled_opacity, scaled_opacity, 0)
        )
        surface.blit(text_surf, self.Position)

    def floatText(self, text):
        self.Text = text
        self.Opacity = 1.0
        self.Position = self.StartPosition


class tTimer:
    def __init__(self, timeout, action):
        self.Timeout = timeout
        self.Action = action
        tUserInterface.Instance.add(self)

    def step(self, seconds):
        self.Timeout -= seconds
        if self.Timeout < 0:
            tUserInterface.Instance.remove(self)
            self.Action()


class tUserInterface:
    Instance = None

    def __init__(self):
        self.MouseEventReceivers = [[]]
        self.TickReceivers = [[]]
        self.Renderables = [[]]
        self.Screen = None
        self.QuitFlag = [False]
        self.Clock = pygame.time.Clock()
        self.EventHandlers = []

        global UI
        if tUserInterface.Instance is not None:
            raise RuntimeError("tUserInterface is a singleton")
        tUserInterface.Instance = self

    def setScreen(self, screen):
        self.Screen = screen

    def newLevel(self):
        def duplicateLevel(ui_array):
            ui_array.insert(0, ui_array[0][:])

        duplicateLevel(self.MouseEventReceivers)
        duplicateLevel(self.TickReceivers)
        duplicateLevel(self.Renderables)
        self.QuitFlag.insert(0, False)

    def discardLevel(self):
        self.MouseEventReceivers.pop(0)
        self.TickReceivers.pop(0)
        self.Renderables.pop(0)
        self.QuitFlag.pop(0)

    def add(self, element):
        def hasMember(element, name):
            for (mem_name, value) in inspect.getmembers(element):
                if mem_name == name:
                    return True
            return False

        if hasMember(element, "render"):
            self.Renderables[0].append(element)
        if hasMember(element, "step"):
            self.TickReceivers[0].append(element)
        if hasMember(element, "buttonDown") or hasMember(element, "mouseMove"):
            self.MouseEventReceivers[0].append(element)

    def addList(self, list):
        for i in list:
            self.add(i)

    def remove(self, element):
        if element in self.MouseEventReceivers[0]:
            self.MouseEventReceivers[0].remove(element)
        if element in self.TickReceivers[0]:
            self.TickReceivers[0].remove(element)
        if element in self.Renderables[0]:
            self.Renderables[0].remove(element)

    def removeAllEventReceivers(self):
        self.MouseEventReceivers[0] = []

    def quit(self, retval=True):
        self.QuitFlag[0] = retval

    def installEventHandler(self, event_type, handler):
        self.EventHandlers.append((event_type, handler))

    def loop(self):
        if self.Screen is None:
            raise RuntimeError("Screen is still unset")

        while not self.QuitFlag[0]:
            seconds = float(self.Clock.tick(60)) / 1000

            for event in pygame.event.get():
                mer = self.MouseEventReceivers[0]

                if event.type == QUIT:
                    self.QuitFlag[0] = True
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    self.QuitFlag[0] = True
                elif event.type == MOUSEBUTTONDOWN:
                    if MOUSE_GRAB is not None:
                        MOUSE_GRAB.buttonDown(event.pos, event.button)
                    else:
                        for obj in mer:
                            if obj.buttonDown(event.pos, event.button):
                                break
                elif event.type == MOUSEBUTTONUP:
                    if MOUSE_GRAB is not None:
                        MOUSE_GRAB.buttonUp(event.pos, event.button)
                    else:
                        for obj in mer:
                            if obj.buttonUp(event.pos, event.button):
                                break
                elif event.type == MOUSEMOTION:
                    if MOUSE_GRAB is not None:
                        MOUSE_GRAB.mouseMove(event.pos)
                    else:
                        for obj in mer:
                            if obj.mouseMove(event.pos):
                                break
                else:
                    for (type, handler) in self.EventHandlers:
                        if event.type == type:
                            handler(event)

            for obj in self.TickReceivers[0]:
                obj.step(seconds)

            for obj in self.Renderables[0]:
                obj.render(self.Screen)

            pygame.display.flip()

        return self.QuitFlag[0]
