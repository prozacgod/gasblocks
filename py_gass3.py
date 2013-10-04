#!/usr/bin/env python
import random
import pygame
from pygame.locals import *
pygame.init()

Font = pygame.font.SysFont("Arial", 15)

random.SystemRandom()

size = (1280, 1280)
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
    
  def replace(self, instance):
    if self.gameGrid:
      self.gameGrid[self.x, self.y] = instance
      
    return instance

class AmberCell(BaseCell):
  def __init__(self, gameGrid=None):
    pass
    
  def getColor(self):
    return (255,255,0)
                          
class GasCell(BaseCell):
  def __init__(self, gameGrid=None):
    BaseCell.__init__(self, gameGrid)
    self.heat = 100
    self.pressure = 0

  def getDebug(self):
    return BaseCell.getDebug(self) + [
      "   Pressure: " + str(self.pressure),
      "   Heat: " + str(self.heat),
    ]

  def getColor(self):
    heat = (100-self.heat) * 3.59

    if heat <= 0:
      eat = 0
      
    if heat >= 360:
      heat = 359
      
    pres = (self.pressure * 10)+50
    if pres > 99:
      pres = 99
      
    if self.pressure == 0:
      pres = 50      
      
    colp = pygame.Color(0,0,0,0)
    colp.hsva = (self.heat, 99, pres)
    return colp
    
  def crystalize1(self):
    """Checks the surrounding neighbors for impurities, anything other than gas"""
    global foaming

    neighbors = self.getNeighbors()
    for n in neighbors:
      if not isinstance(n, GasCell):
        self.replace(AmberCell())
        foaming = False
        return
        
  def crystalize(self):
    return
    
    neighbors = self.getNeighbors()
    
    for n in neighbors:
      if isinstance(n, GasCell):
        if n.crystalized or n.crystalization > 0:
          self.crystalization = 1
          return 
      else:
        self.crystalization = 1
        return 
   
  def update(self):
    if self.heat > 10 and self.pressure > 0:
      neighbors = self.getNeighbors()
      #randomize this for fringe edges to not have an affinity!
      random.shuffle(neighbors)

      gasNeighbors = [n for n in neighbors if isinstance(n, GasCell)]
      
      # spread into all my air neighbors
      newNeighbors = []
      for neighbor in neighbors:
        if self.pressure > 0:
          if isinstance(neighbor, EmptyCell):
            newGas = GasCell()
            self.pressure -= 1
            neighbor.replace(newGas)
            newNeighbors += [newGas]
        else:
          break                      

      # if I still have pressure spread into ALL gas cells around me
      if len(gasNeighbors) > 0:
        while self.pressure > 0:
          r = random.randint(0, len(gasNeighbors) - 1)
          ncell = gasNeighbors[r]
          if len(newNeighbors) == 0 or self.pressure < ncell.pressure:
            ncell.pressure += 1
            self.pressure -= 1
          else:
            random.choice(newNeighbors).pressure += 1
            self.pressure -= 1
      
    if self.heat > 0:
      self.heat -= 1
    else:
      self.crystalize()
      

class HardCell(BaseCell):
  def getColor(self):
    return (0,255,0)

class EmptyCell(BaseCell):
  def getColor(self):
    return (50,50,50)
      
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
    gasCells = []
    for row in self.cells:
      for cell in row:
        if isinstance(cell, GasCell):
          gasCells += [cell]
          
    for gasCell in gasCells:
      gasCell.update()
         
  def worldData(self):
    pressure = 0
    volume = 0
    for row in self.cells:
      for cell in row:
        if isinstance(cell, GasCell):
          volume += 1
          pressure += cell.pressure

    return ["World Data: ",  "   pressure:" + str(pressure), "   volume: " + str(volume)]
  
foaming = True
drawing = False

def processEvent(gg, event):
  global running
  global foaming
  global drawing
  
  if event.type == QUIT:
    running = False
      
  elif event.type == KEYDOWN:
    if event.key == K_ESCAPE:
      running = False
    if event.key == K_SPACE:
      gg.update();
    if event.key == K_f:
      foaming = not foaming
          
  elif event.type == MOUSEBUTTONDOWN:
    x = event.pos[0]/cellSize
    y = event.pos[1]/cellSize
    cell = gg[x,y]
    if event.button == 1:
      if isinstance(cell, EmptyCell):
        gg[x,y] = HardCell()
      else:
        gg[x,y] = EmptyCell()

    elif event.button == 3:
      cell = GasCell()
      gg[x,y] = cell

      cell.pressure = 256;
      cell.heat = 100;

  #elif event.type == MOUSEBUTTONUP:


def processEvents(gg):
  for event in pygame.event.get():
    processEvent(gg, event)
        
running = True

def updateData(gg):
  global screen
  global clock
  global foaming

  messages = [
    "FPS: " + str(int(clock.get_fps())) + (" Animating!" if foaming else "")
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


def main():
  global running
  global clock
  global foaming
  clock = pygame.time.Clock()

  gg = GameGrid(size[0]/cellSize, size[1]/cellSize)
  while running:
    processEvents(gg)
    screen.fill((0,0,0))

    gg.render(screen)

    if foaming:
      gg.update();

    #gg.renderFoam(screen)
    updateData(gg)
    
     
    pygame.display.flip();
    clock.tick(10)

main()
