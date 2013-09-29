#!/usr/bin/env python
import pygame
from pygame.locals import *
pygame.init()

Font = pygame.font.SysFont("Arial", 15)

size = (800, 800)
cellSize = 8
screen = pygame.display.set_mode(size)

def drawText(pos, text, color=(255,255,255), background=None):
  global Font
  global screen
  if background:
    label = Font.render(text, True, color, background)
  else:
    label = Font.render(text, True, color)
  screen.blit(label, pos)
                        
class GasCell:
  def __init__(self):
    self.heat = 0
    self.pressure = 0

  def getColor(self):
    return (255,255,0)

class HardCell:
  def __init__(self):
    pass

  def getColor(self):
    return (0,255,0)

class EmptyCell:
  def __init__(self):
    pass
  
  def getColor(self):
    return (50,50,50)

class GameGrid:
  def __init__(self, w, h):
    self.cells = [[EmptyCell() for x in range(w)] for y in range(h)]
      
  def __getitem__(self, key):
    if (key[0] < 0):
      return HardCell();

    if (key[1] < 0):
      return HardCell();

    if (key[0] >= len(self.cells)):
      return HardCell();

    if (key[1] >= len(self.cells[0])):
      return HardCell();

    return self.cells[key[1]][key[0]]
  
  def __setitem__(self, key, value):
    self.cells[key[1]][key[0]] = value
    
  def render(self, surface):
    x = 0
    y = 0
    for row in self.cells:
      x = 0
      for cell in row:
        surface.fill(cell.getColor(), (x * cellSize, y * cellSize, cellSize-1, cellSize-1))
        x = x + 1
      y = y + 1

  def update(self):
    #update self.cells here
    pass
      
def processEvent(gg, event):
  global running
  if event.type == QUIT:
    running = False
      
  elif event.type == KEYDOWN:
    if event.key == K_ESCAPE:
      running = False
    if event.key == K_SPACE:
      gg.update();
          
  elif event.type == MOUSEBUTTONDOWN:
    x = event.pos[0]/cellSize
    y = event.pos[1]/cellSize
    cell = gg[x,y]
    if event.button == 1:
      if isinstance(cell, HardCell):
        gg[x,y] = EmptyCell()
      if isinstance(cell, EmptyCell):
        gg[x,y] = HardCell()
    elif event.button == 3:
      cell = GasCell()
      gg[x,y] = cell
      cell.pressure = 256;
      cell.heat = 128;
      
  #elif event.type == MOUSEBUTTONUP:


def processEvents(gg):
  for event in pygame.event.get():
    processEvent(gg, event)
        
running = True

def updateData(gg):
  """Information overlay goes here"""
  global screen
  global clock
  pos = pygame.mouse.get_pos()
  
  cellx = pos[0] / cellSize
  celly = pos[1] / cellSize
  
  cell = gg[cellx, celly]
  
  messages = [
    "Cell: " + cell.__class__.__name__,
    "FPS: " + str(int(clock.get_fps()))
  ]
   
  # add messages here to display them :P


  #draws messages            
  y = 5
  for message in messages:
    drawText((5,y), message)
    y = y + 20


def main():
  global running
  global clock
  clock = pygame.time.Clock()

  gg = GameGrid(size[0]/cellSize, size[1]/cellSize)
  while running:
    processEvents(gg)
    screen.fill((0,0,0))

    gg.render(screen)
    updateData(gg)
     
    pygame.display.flip();
    clock.tick(60)

main()
