from stone import *


def findDestructionCandidates(field):
    width = len(field)
    height = len(field[0])

    if not field:
        return []

    result = []
    for x in range(0, width):
        row = [(x, 0)]
        last_type = field[x][0].type()
        for y in range(1, height):
            if field[x][y].type() == last_type:
                row.append((x, y))
            else:
                if len(row) >= 3:
                    result.extend(row)
                row = [(x, y)]
                last_type = field[x][y].type()
        if len(row) >= 3:
            result.extend(row)

    for y in range(0, height):
        row = [(0, y)]
        last_type = field[0][y].type()
        for x in range(1, width):
            if field[x][y].type() == last_type:
                row.append((x, y))
            else:
                if len(row) >= 3:
                    result.extend(row)
                row = [(x, y)]
                last_type = field[x][y].type()
        if len(row) >= 3:
            result.extend(row)

    # sort result is in y-ascending order.
    result.sort(key=lambda tup: tup[::-1])

    # weed out duplicates
    last = None
    newresult = []
    for item in result:
        if last != item:
            newresult.append(item)
            last = item

    return newresult


def destroyStones(field, candidates):
    for (x, y) in candidates:
        field[x][1 : y + 1] = field[x][0:y]
        field[x][0] = tStone()


def copyField(field):
    newfield = []
    for column in field:
        newcolumn = []
        for stone in column:
            newcolumn.append(stone)
        newfield.append(newcolumn)

    return newfield


def swapStones(field, start_x, start_y, end_x, end_y):
    temp = field[end_x][end_y]
    field[end_x][end_y] = field[start_x][start_y]
    field[start_x][start_y] = temp


# tPlayingField ---------------------------------------------------------------
class tPlayingField:
    def __init__(self, position, width, height):
        self.Position = position
        self.GridX = 55
        self.GridY = 55
        self.Width = width
        self.Height = height
        self.MoveDoneHooks = [lambda x: self.mouseMove(pygame.mouse.get_pos())]
        self.HintsDoneHooks = []

        self.initialize()

    def initialize(self):
        self.UIEnabledCounter = 1
        self.WaitAndCheckMode = 1
        self.StartDragIndex = None

        self.Hints = []
        self.HintToDo = []
        self.ShownHints = []
        self.ConsumableHints = []

        self.KeepAliveList = []

        self.Field = []

        self.StonesClearedThisMove = 0

        self.ActiveStone = None

        self.GameBegun = False

    def newGame(self):
        self.initialize()

        for x in range(0, self.Width):
            column = []
            for y in range(0, self.Height):
                stone = tStone()
                stone.setPosition((x * self.GridX, (y - self.Height) * self.GridY))
                stone.setVelocity((0, 0))
                stone.setAcceleration((0, 3000))
                stone.setStopPosition((x * self.GridX, y * self.GridY), 1)
                stone.setMoveDelay((self.Height - y) * 0.04)
                column.append(stone)
            self.Field.append(column)

    # externally accessible -----------------------------------------------------
    def width(self):
        return self.Width

    def height(self):
        return self.Height

    def field(self, x, y):
        return self.Field[x][y]

    def hints(self):
        return self.Hints

    def isUIEnabled(self):
        return self.UIEnabledCounter == 0

    def disableUI(self):
        self.UIEnabledCounter += 1

        if self.ActiveStone:
            self.ActiveStone.resetAnimation()
            self.ActiveStone = None

    def enableUI(self):
        self.UIEnabledCounter -= 1

    def hasGameBegun(self):
        return self.GameBegun

    def isActive(self):
        return len(self.Field) != 0

    def isReadyForUserInteraction(self):
        return self.isUIEnabled() and not self.StartDragIndex

    def addMoveDoneHook(self, hook):
        self.MoveDoneHooks.append(hook)

    def addHintsDoneHook(self, hook):
        self.HintsDoneHooks.append(hook)

    def clearHintsDoneHooks(self):
        self.HintsDoneHooks = []

    def showHint(self):
        if (
            self.isUIEnabled()
            and self.Hints
            and not self.StartDragIndex
            and not self.HintToDo
        ):
            for i in self.ShownHints:
                i.setBlinking(0)

            if len(self.ConsumableHints) == 0:
                self.ConsumableHints = self.Hints[:]

            ((hint_x1, hint_y1), (hint_x2, hint_y2)) = self.ConsumableHints[0]
            self.ConsumableHints.pop(0)

            self.ShownHints = [
                self.Field[hint_x1][hint_y1],
                self.Field[hint_x2][hint_y2],
            ]
            for i in self.ShownHints:
                i.setBlinking(1)
            return True
        else:
            return False

    def executeMove(self, xxx_todo_changeme2):
        ((start_x, start_y), (end_x, end_y)) = xxx_todo_changeme2
        self.StonesClearedThisMove = 0

        dx = end_x - start_x
        dy = end_y - start_y

        valid = 0
        if dx * dx == 1 and dy * dy == 0:
            valid = 1
        if dx * dx == 0 and dy * dy == 1:
            valid = 1
        if not valid:
            SOUND_INVALID.get().play()
            return 1

        if self.ActiveStone:
            self.ActiveStone.stopAnimation()
            self.ActiveStone = None

        for i in self.ShownHints:
            i.setBlinking(0)
        self.ShownHints = []

        newfield = copyField(self.Field)

        start_stone = newfield[start_x][start_y]
        end_stone = newfield[end_x][end_y]

        swapStones(newfield, start_x, start_y, end_x, end_y)

        candidates = findDestructionCandidates(newfield)
        if len(candidates) == 0:
            SOUND_INVALID.get().play()
            return 1

        start_stone.setAcceleration((dx * 1000, dy * 1000))
        start_stone.setStopPosition((end_x * self.GridX, end_y * self.GridY), 0)

        end_stone.setAcceleration((-dx * 1000, -dy * 1000))
        end_stone.setStopPosition((start_x * self.GridX, start_y * self.GridY), 0)

        self.Field = newfield

        self.disableUI()
        self.WaitAndCheckMode = 1

    def blowUp(self):
        self.disableUI()

        x = 0
        for i in self.Field:
            y = 0
            for j in i:
                j.disableStopPosition()
                j.setVelocity(
                    (
                        (x - (self.width() - 1) / 2.0) * 120.0 + random.uniform(0, 90),
                        (y - (self.height() - 5) / 2.0) * 180.0 + random.uniform(0, 90),
                    )
                )
                j.setAcceleration((0, 600))
                y += 1
            x += 1

    # more or less internal -----------------------------------------------------
    def render(self, surface):
        for i in self.Field:
            for j in i:
                j.render(surface, self.Position)

        for i in self.KeepAliveList:
            i.render(surface, self.Position)

    def step(self, seconds):
        # maintain keepalive list
        new_keep_alive_list = []
        for i in self.KeepAliveList:
            i.step(seconds)
            if i.needsToStayAlive():
                new_keep_alive_list.append(i)
        self.KeepAliveList = new_keep_alive_list

        # check if something is still moving
        still_on_the_move = 0

        for i in self.Field:
            for j in i:
                j.step(seconds)
                if j.isOnTheMove():
                    still_on_the_move = 1

        # if not, check and destroy or enable ui
        if not (still_on_the_move) and self.WaitAndCheckMode:
            if not self.checkAndDestroyStones():
                self.enableUI()
                self.WaitAndCheckMode = 0
                for hook in self.MoveDoneHooks:
                    hook(self.StonesClearedThisMove)

                self.GameBegun = True

                self.startGeneratingHints()

        # generate hints
        if self.GameBegun:
            self.generateHints()

    def getGridIndex(self, position):
        (myx, myy) = self.Position
        (mx, my) = position
        mx -= myx
        my -= myy

        if mx < 0 or mx >= self.GridX * self.Width:
            return None
        elif my < 0 or my >= self.GridY * self.Height:
            return None
        else:
            return (mx // self.GridX, my // self.GridY)

    def buttonDown(self, position, button):
        if not self.isUIEnabled():
            return 0

        if button != 1:
            return 0

        self.StartDragIndex = self.getGridIndex(position)
        if self.StartDragIndex is None:
            return 0

        (x, y) = self.StartDragIndex
        return 1

    def buttonUp(self, position, button):
        if self.StartDragIndex is None:
            return 0

        if button != 1:
            return 0

        (start_x, start_y) = self.StartDragIndex
        self.StartDragIndex = None

        stop_drag_index = self.getGridIndex(position)
        if stop_drag_index is None:
            return 0

        (end_x, end_y) = stop_drag_index

        self.executeMove(((start_x, start_y), (end_x, end_y)))
        return 1

    def mouseMove(self, position):
        if not self.Field or self.StartDragIndex or not self.isUIEnabled():
            return

        grid = self.getGridIndex(position)
        if grid:
            (x, y) = grid
            prev_active = self.ActiveStone
            self.ActiveStone = self.Field[x][y]
            if self.ActiveStone != prev_active:
                if prev_active:
                    prev_active.resetAnimation()
                self.ActiveStone.animate()
        else:
            if self.ActiveStone:
                self.ActiveStone.resetAnimation()
                self.ActiveStone = None

    def checkAndDestroyStones(self):
        candidates = findDestructionCandidates(self.Field)

        # This subroutine depends on the fact that findDestructionCandidates
        # returns a y-ascending list

        newstonecount = [0] * self.Width

        self.StonesClearedThisMove += len(candidates)

        for (x, y) in candidates:
            SOUNDMGR_DESTROY.get().play()

            stone = self.Field[x][y]
            stone.startShrinking()
            self.KeepAliveList.append(stone)

            self.Field[x][1 : y + 1] = self.Field[x][0:y]
            for ynew in range(1, y + 1):
                moving_stone = self.Field[x][ynew]
                moving_stone.setAcceleration((0, 1000))
                moving_stone.setStopPosition((0, ynew * self.GridY), 1)
                moving_stone.setMoveDelay(0.2)

            newstonecount[x] += 1

            newstone = tStone()
            newstone.setPosition((x * self.GridX, -self.GridY * newstonecount[x]))
            newstone.setVelocity((0, 0))
            newstone.setAcceleration((0, 1000))
            newstone.setStopPosition((x * self.GridX, 0), 1)
            newstone.setMoveDelay(0.2)
            self.Field[x][0] = newstone

        return len(candidates)

    def tryMove(self, x1, y1, x2, y2):
        if not (0 <= x1 < self.Width):
            return 0
        if not (0 <= x2 < self.Width):
            return 0
        if not (0 <= y1 < self.Height):
            return 0
        if not (0 <= y2 < self.Height):
            return 0

        swapStones(self.Field, x1, y1, x2, y2)
        candidates = findDestructionCandidates(self.Field)
        swapStones(self.Field, x1, y1, x2, y2)
        return len(candidates)

    def startGeneratingHints(self):
        self.ConsumableHints = []
        self.Hints = []

        for x in range(0, self.Width):
            for y in range(0, self.Height):
                self.HintToDo.append((x, y))

    def generateHints(self):
        if not self.Field:
            return

        if len(self.HintToDo) != 0:
            (x, y) = self.HintToDo.pop(0)

            if x + 1 < self.Width and self.tryMove(x, y, x + 1, y):
                self.Hints.append(((x, y), (x + 1, y)))
            if y + 1 < self.Height and self.tryMove(x, y, x, y + 1):
                self.Hints.append(((x, y), (x, y + 1)))

            if len(self.HintToDo) == 0:
                self.ConsumableHints = self.Hints[:]
                for hook in self.HintsDoneHooks:
                    hook()
