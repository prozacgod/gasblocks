#!/usr/bin/env python
import random
import pygame
from pygame.locals import *
pygame.init()

Font = pygame.font.SysFont("Arial", 15)

size = (1024,1024)
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
                        
class GasCell:
  def __init__(self):
    self.heat = 0
    self.pressure = 0

  def getColor(self):
    p = 128 + self.pressure/2 
    if p < 0:
      p = 10
      
    if p > 255:
      p = 255
    return (p, p, 0)

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

class GasGroup:
  def __init__(self):
    self.sources = []
    self.dests = []
   
  def addDest(self, dest, sources):
    valid = False
    for adest in self.dests:  
      distx = adest[0] - dest[0]
      disty = adest[1] - dest[1]
      if ((abs(distx) <= 1) and (abs(disty) <= 1)):
         valid = True

    if (len(self.dests) == 0):
      valid = True

    if valid:
      self.dests += [dest]
      for source in sources:
        if not source in self.sources:
          self.sources += [source]
      
    return valid
    #if (source in self.source):

  def containsDest(self, x, y):
    return (x,y) in self.dests

  def containsSource(self, x, y):
    return (x,y) in self.sources

      
class GameGrid:
  def __init__(self, w, h):
    self.cells = [[EmptyCell() for x in range(w)] for y in range(h)]
    self.updates = []
    self.groups = []
      
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
      
  def updateGas(self):
    # Find all blocks we want to spread into
    updates = {}
    x = 0
    y = 0
    for row in self.cells:
      x = 0
      for cell in row:
        if isinstance(cell, GasCell) and cell.pressure > 0:
          for ix in range(-1,2):
            for iy in range(-1,2):
              if not (ix == 0 and iy == 0):
                xx = ix + x
                yy = iy + y
                if isinstance(self[xx, yy], EmptyCell):
                  if not (xx, yy) in updates:
                    updates[(xx, yy)] = []
                    
                  updates[(xx, yy)] += [(x,y)]

        x = x + 1
      y = y + 1
      
    # Once we have these blocks we seperate them into groups, their source blocks 
    # contribute collectively to their expansion powers.
    groups = []
    currentUpdate = updates.keys()

    gasg = GasGroup()
    while len(currentUpdate) > 0:
      # this is a bit of a hack, forces a new GasGroup to only be created when we've
      # exhauasted the list of available destinations, after iterating the list

      createNewGroup = True

      nextUpdate = []
      for update in currentUpdate:
        if not gasg.addDest(update, updates[update]):
          nextUpdate += [update]
        else:
          createNewGroup = False

      if createNewGroup:
        groups += [gasg]
        gasg = GasGroup()

      currentUpdate = nextUpdate;
    
    if not gasg in groups:
      groups += [gasg]
      
    #now that the groups have been determined...
    print "groups: ", len(groups)

    #we need to distribute the gas "pressure" to all the targets
    for group in groups:
      if len(group.sources) == 0:
        continue

      if len(group.dests) == 0:
        continue
        
      #Calculate the pressure being contributed to this group        

      groupPressure = 0
      for source in group.sources:
        sourceCell = self[source[0], source[1]]
        groupPressure += sourceCell.pressure
        sourceCell.pressure = 0
        
      groupPressure = groupPressure - len(group.sources)

      #we need to "regroup" into "dest & source" distinct array to get a count
      #TODO: lookup 'sets' instead of dict
      dest_sources = {}
      for dest in group.dests:
        for source in updates[dest]:
          dest_sources[dest + source] = True
      
      avgPressure = groupPressure / len(group.dests)
      remainPressure = groupPressure % len(group.dests)

      print "total cells that need pressure", len(dest_sources)
      print "group pressure", groupPressure
      print "avg Pressure", avgPressure
      print "remaining Pressure", remainPressure
      
      for ds in dest_sources.keys():
        print "cell sources ", updates[ds[0], ds[1]]
        destCell = GasCell()
        if isinstance(self[ds[0], ds[1]], GasCell):
          destCell = self[ds[0], ds[1]]
        else:
          self[ds[0], ds[1]] = destCell
          
        destCell.pressure += avgPressure
        
      for i in range(remainPressure):
        dest = random.choice(dest_sources.keys())
        destCell = self[dest[0], dest[1]]
        destCell.pressure += 1
           
    self.groups = groups      
    self.updates = updates
  

  def renderFoam(self, surface):
    for update in self.updates:
      pygame.draw.rect(surface, (255,0,0), (update[0] * cellSize, update[1] * cellSize, cellSize, cellSize), 1)

def processEvent(gg, event):
  global running
  if event.type == QUIT:
    running = False
      
  elif event.type == KEYDOWN:
    if event.key == K_ESCAPE:
      running = False
    if event.key == K_SPACE:
      gg.updateGas();
          
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
  global screen
  global clock
  pos = pygame.mouse.get_pos()
  cellx = pos[0] / cellSize
  celly = pos[1] / cellSize
  
  cell = gg[cellx, celly]
  
  infoStr = ""
  if isinstance(cell, GasCell):
    infoStr = "Pressure: " + str(cell.pressure)
  
  messages = [
    "FPS: " + str(int(clock.get_fps())),
    "Cell: " + cell.__class__.__name__ + " " + infoStr
  ]

  if (cellx, celly) in gg.updates:
    messages += ["Gas Sources"]
    for source in gg.updates[(cellx, celly)]:
      messages += [str(source)]

  if True:
    for group in gg.groups:
      if group.containsDest(cellx, celly):
        messages += ["This is a destination group"]
        messages += ["Sources: " + ",".join([str(source) for source in group.sources])]
        
        for dest in group.dests:
          pygame.draw.rect(screen, (255,255,255), (dest[0] * cellSize, dest[1] * cellSize, cellSize, cellSize), 1)
          
        for source in group.sources:
          screen.fill((0,0,255), (source[0] * cellSize, source[1] * cellSize, cellSize-1, cellSize-1))
            
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
    gg.renderFoam(screen)
    updateData(gg)
     
    pygame.display.flip();
    clock.tick(60)

main()
