import pygame
from pygame.locals import *
pygame.init()

Font = pygame.font.SysFont("Arial", 15)

size = (1024, 1024)
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
        surface.fill(cell.getColor(), (x * 16, y * 16, 15, 15))
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

    print "groups: ", len(groups)
    if (len(groups) > 0):
      print "group len 0", len(groups[0].dests)

    self.groups = groups      
    self.updates = updates
  

  def renderFoam(self, surface):
    for update in self.updates:
      pygame.draw.rect(surface, (255,0,0), (update[0] * 16, update[1] * 16, 16, 16), 1)

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
    x = event.pos[0]/16
    y = event.pos[1]/16
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
  cellx = pos[0] / 16
  celly = pos[1] / 16
  
  cell = gg[cellx, celly]
  
  messages = [
    "Cell: " + cell.__class__.__name__,
    "FPS: " + str(int(clock.get_fps()))
  ]

  if (cellx, celly) in gg.updates:
    messages += ["Gas Sources"]
    for source in gg.updates[(cellx, celly)]:
      messages += [str(source)]

  for group in gg.groups:
    if group.containsDest(cellx, celly):
      messages += ["This is a destination group"]
      messages += ["Sources: " + ",".join([str(source) for source in group.sources])]
      
      for dest in group.dests:
        pygame.draw.rect(screen, (255,255,255), (dest[0] * 16, dest[1] * 16, 16, 16), 1)
        
      for source in group.sources:
        screen.fill((0,0,255), (source[0] * 16, source[1] * 16, 15, 15))
            
  y = 5
  for message in messages:
    drawText((5,y), message)
    y = y + 20


def main():
  global running
  global clock
  clock = pygame.time.Clock()

  gg = GameGrid(size[0]/16, size[1]/16)
  while running:
    processEvents(gg)
    screen.fill((0,0,0))

    gg.render(screen)
    gg.renderFoam(screen)
    updateData(gg)
     
    pygame.display.flip();
    clock.tick(60)

main()
