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

  def update(self):
    return False
    
  def replace(self, instance):
    if self.gameGrid:
      self.gameGrid[self.x, self.y] = instance
      
    return instance
                          
class GasCell(BaseCell):
  def __init__(self, gameGrid=None):
    BaseCell.__init__(self, gameGrid)
    self.heat = 100
    self.pressure = 0

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
    colp.hsva = (self.heat, 99, pres) #if self.t == 3 else 99,99)
    return colp
    
  #def update(self):
  #  if (self.pressure > 0):
  #    ncell = self.gameGrid[self.x - 1, self.y]
  #    if (isinstance(ncell, EmptyCell)):
  #      ncell = ncell.replace(GasCell())
  #      ncell.pressure = self.pressure - 1
  # 
  #   ncell = self.gameGrid[self.x + 1, self.y]
  #    if (isinstance(ncell, EmptyCell)):
  #      ncell = ncell.replace(GasCell())
  #      ncell.pressure = self.pressure - 1
  #   self.pressure = 0

  def update(self):
    if self.pressure > 0:
      #randomize this for fringe edges to not have an affinity!
      neighbors = self.getNeighbors()
      random.shuffle(neighbors)
      airNeighbors = [n for n in neighbors if isinstance(n, EmptyCell)]

      # spread into all my air neighbors
      if (len(airNeighbors)) > 0:
        for n in airNeighbors:
          if self.pressure > 0:
            newGas = GasCell()
            newGas.pressure = 1
            self.pressure -= 1
            n.replace(newGas)
          else:
            break                      

        #pn = min(self.pressure-1, len(airNeighbors))
        #for i in range(pn):
        #  newGas = GasCell()
        #  newGas.pressure += 1
        #  self.pressure -= 1
        #  airNeighbors[i].replace(newGas)

      # if I still have pressure spread into ALL gas cells around me
      if self.pressure > 0:
          neighbors = self.getNeighbors()
          gasNeighbors = [n for n in neighbors if isinstance(n, GasCell)]

          while self.pressure > 0:
            r = random.randint(0, len(gasNeighbors) - 1)
            ncell = gasNeighbors[r]
            ncell.pressure += 1
            self.pressure -= 1
            
    if self.heat > 0:
      self.heat -= 5

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
    self.updates = {}
    self.updating = False

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
    if self.updating:
      self.updates[key] = value
    else:      
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
        surface.fill(cell.getColor(), (x * cellSize, y * cellSize, cellSize-1, cellSize-1))
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

  def updateGasOld(self):
    # Find all blocks we want to spread into
    sources = {}
    gas_sources = {}
    x = 0
    y = 0
    for row in self.cells:
      x = 0
      for cell in row:
        # cells with pressure
        if isinstance(cell, GasCell):
          #if (cell.heat < 50) and (cell.pressure > 0):
          #  cell.pressure -= 1
        
          if cell.heat > 0 and not (x, y) in sources:
            sources[(x, y)] = []

          if cell.heat > 0 and not (x, y) in gas_sources:
            gas_sources[(x, y)] = []


          if cell.pressure > 0:
            for ix in range(-1,2):
              for iy in range(-1,2):
                if not (ix == 0 and iy == 0):
                  xx = ix + x
                  yy = iy + y
                  ncell = self[xx,yy]
                  
                  if isinstance(ncell, EmptyCell):
                    if not (xx, yy) in sources[x,y]:
                      sources[x,y] += [(xx,yy)]
                      
                  if isinstance(ncell, GasCell) and ncell.heat < 90:
                    if not (xx, yy) in gas_sources[x,y]:
                      gas_sources[x,y] += [(xx,yy)]

          if cell.heat > 0:
            cell.heat -= 5
          #reduce heat in all existing blocks

        x = x + 1
      y = y + 1
      
    for source_pos in sources:
      source = self[source_pos[0], source_pos[1]]
      dests = sources[source_pos]
      for dest_pos in dests:
        if isinstance(self[dest_pos[0], dest_pos[1]], EmptyCell):
          dest = GasCell()
          self[dest_pos[0], dest_pos[1]] = dest
          dest.heat = 100

      if source.pressure > 0 and len(dests) > 0:
        source.pressure -= 1
        
        pressure = source.pressure - random.randint(0,5)
        source.pressure -= pressure
        while pressure > 0:
          pressure -= 1
          adest = random.choice(dests)
          self[adest[0], adest[1]].pressure += 1

    # interior gas pressures
    for source_pos in gas_sources:
      source = self[source_pos[0], source_pos[1]]
      dests = gas_sources[source_pos]
      #for dest_pos in dests:
      #  dest = self[dest_pos[0], dest_pos[1]]
      #  if isinstance(dest, GasCell) and dest.heat == 100:
      #    dest.pressure += source.pressure
      #    source.pressure = 0
      #   break;
      
      if source.pressure > 0 and len(dests) > 0:
        adest = random.choice(dests)
        self[adest[0], adest[1]].pressure += source.pressure
        source.pressure = 0
         
  def worldData(self):
    pressure = 0
    volume = 0
    for row in self.cells:
      for cell in row:
        if isinstance(cell, GasCell):
          volume += 1
          pressure += cell.pressure

    return {"pressure": pressure, "volume": volume}
  
foaming = False
foaming_frame = 0
def processEvent(gg, event):
  global running
  global foaming
  
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
      if isinstance(cell, HardCell):
        gg[x,y] = EmptyCell()
      if isinstance(cell, EmptyCell):
        gg[x,y] = HardCell()
    elif event.button == 3:
      cell = GasCell()
      gg[x,y] = cell

      cell.pressure = 10;
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
  pos = pygame.mouse.get_pos()
  cellx = pos[0] / cellSize
  celly = pos[1] / cellSize
  
  cell = gg[cellx, celly]
  
  infoStr = "World Pressure: " + str(gg.worldData())
  if isinstance(cell, GasCell):
    infoStr += "Pres: " + str(cell.pressure)
    infoStr += " Heat: " + str(cell.heat)
  
  messages = [
    "FPS: " + str(int(clock.get_fps())) + (" Animating!" if foaming else ""),
    "Cell: " + cell.__class__.__name__ + " " + infoStr,
    "Air: " + str(len([n for n in cell.getNeighbors() if isinstance(n, EmptyCell)]))
  ]

  #if (cellx, celly) in gg.updates:
  #  messages += ["Gas Sources"]

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
