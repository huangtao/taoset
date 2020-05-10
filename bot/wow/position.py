import pygame


class Positioner:

    def __init__(self, surface):
        self.surface = surface
        self.x = 0
        self.y = 0
        self.oldX = 0
        self.oldY = 0
        self.direction = 0

    def updateDirection(self, directionVal):
        # 如果传入负值并且调整后为负
        if (self.direction + directionVal < 0):
            self.direction = 360 + directionVal

        # 超过360调整
        elif (self.direction + directionVal > 360):
            self.direction = 360 - self.direction + directionVal

        else:
            self.direction += directionVal

    def updatePosition(self):
        self.oldX = self.x
        self.oldY = self.y

        if (self.direction == 0):
            self.x += 0
            self.y += 6

    def drawLinesFromData(self):
        width, height = self.surface.get_size()
        halfWidth = int(width / 2)
        halfHeight = int(height / 2)

        pygame.draw.line(self.surface, (0, 0, 0), (halfWidth+self.oldX,
                                                   halfHeight+self.oldY), (halfWidth+self.x, halfHeight+self.y), 2)
