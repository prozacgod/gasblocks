#!/usr/bin/env python
import random
import pygame
from pygame.locals import *
pygame.init()

Font = pygame.font.SysFont("Tahoma", 15)

random.SystemRandom()

size = (1280, 1280)
cellSize = 16
screen = pygame.display.set_mode(size)

def drawText(pos, text, color=(255,255,255), background=None):
  global Font
  global screen
  if background:
    label = Font.render(text, True, color, background)
  else:
    label = Font.render(text, True, color)

  screen.blit(label, pos)
                    
class BaseCell:
  def __init__(self, gameGrid = None):
    self.gameGrid = gameGrid
    self.x = 0
    self.y = 0
    
  def render(self, surface):
    surface.fill(self.getColor(), (self.x * cellSize, self.y * cellSize, cellSize-1, cellSize-1))
    
  def getNeighbors(self):
    if not self.gameGrid:
      return []

    return [
      self.gameGrid[self.x - 1, self.y - 1],
      self.gameGrid[self.x, self.y - 1],
      self.gameGrid[self.x + 1, self.y - 1],
      self.gameGrid[self.x - 1, self.y],
      self.gameGrid[self.x + 1, self.y],
      self.gameGrid[self.x - 1, self.y + 1],
      self.gameGrid[self.x, self.y + 1],
      self.gameGrid[self.x + 1, self.y + 1]
    ]
    
  def getDebug(self):
    return [
      "Cell: " + self.__class__.__name__,
      "   Air: " + str(len([n for n in self.getNeighbors() if isinstance(n, EmptyCell)]))
    ]
  
  def update(self):
    return False

  def keyDown(self, key):
    pass

  def keyUp(self, key):
    pass
    
  def mouseDown(self, button):
    pass
    
  def mouseUp(self, button):
    pass
    
  def replace(self, instance):
    if self.gameGrid:
      self.gameGrid[self.x, self.y] = instance
      
    return instance

class HardCell(BaseCell):
  def getColor(self):
    return (0,255,0)

  def mouseUp(self, button):
    self.replace(EmptyCell())


class EmptyCell(BaseCell):
  def getColor(self):
    return (50,50,50)

  def mouseUp(self, button):
    self.replace(HardCell())
      
class GameGrid:
  def __init__(self, w, h):
    self.w = w
    self.h = h

    self.cells = [[EmptyCell(self) for x in range(w)] for y in range(h)]
    for y in range(h):
      for x in range(w):
        self[x,y] = EmptyCell(self)
        
  def clone(self):
    gg = GameGrid(self.w, self.h)
    gg.cells = [cell for cell in [row for row in self.cells]]
    return gg

  def __getitem__(self, key):
    if (key[0] < 0):
      return HardCell(None);

    if (key[1] < 0):
      return HardCell(None);

    if (key[0] >= len(self.cells)):
      return HardCell();

    if (key[1] >= len(self.cells[0])):
      return HardCell();

    cell = self.cells[key[1]][key[0]]
    cell.gameGrid = self
    cell.x = key[0]
    cell.y = key[1]
    return cell

  def __setitem__(self, key, value):
    value.x = key[0]
    value.y = key[1]
    value.gameGrid = self
    self.cells[key[1]][key[0]] = value
    
  def render(self, surface):
    x = 0
    y = 0
    for row in self.cells:
      x = 0
      for cell in row:
        cell.render(surface)
        x = x + 1
      y = y + 1
      
  def update(self):
    pass
             
  def worldData(self):
    return ["No data"]
  
def processEvent(gg, event):
  global running
  
  if event.type == QUIT:
    running = False
      
  elif event.type == KEYDOWN:
    if event.key == K_ESCAPE:
      running = False
    elif event.key == K_SPACE:
      gg.update();
    else:
      pos = pygame.mouse.get_pos()
      cellx = pos[0] / cellSize
      celly = pos[1] / cellSize
      
      gg[cellx, celly].keyDown(evt.key)

  elif event.type == KEYUP:
    pos = pygame.mouse.get_pos()
    cellx = pos[0] / cellSize
    celly = pos[1] / cellSize
    
    gg[cellx, celly].keyUp(evt.key)
  
          
  elif event.type == MOUSEBUTTONDOWN:
    x = event.pos[0]/cellSize
    y = event.pos[1]/cellSize
    gg[x,y].mouseDown(event.button)
  elif event.type == MOUSEBUTTONUP:
    x = event.pos[0]/cellSize
    y = event.pos[1]/cellSize
    gg[x,y].mouseUp(event.button)

def processEvents(gg):
  for event in pygame.event.get():
    processEvent(gg, event)
        

def debugOverlay(gg):
  global screen
  global clock

  messages = [
    "FPS: " + str(int(clock.get_fps()))
  ] + gg.worldData()


  pos = pygame.mouse.get_pos()
  cellx = pos[0] / cellSize
  celly = pos[1] / cellSize
  
  cell = gg[cellx, celly]
  
  messages += cell.getDebug()

  y = 5
  for message in messages:
    drawText((5,y), message)
    y = y + 20

def metaOverlay():
  global screen, size  
  screen.fill((0,0,0), (size[0] - 32 - 10, 10, 32, 256))

running = True
def main():
  global running
  global clock
  clock = pygame.time.Clock()

  gg = GameGrid(size[0]/cellSize, size[1]/cellSize)
  while running:
    processEvents(gg)
    screen.fill((0,0,0))

    gg.render(screen)
    gg.update();
    metaOverlay()
    debugOverlay(gg)
     
    pygame.display.flip();
    clock.tick(10)

main()
