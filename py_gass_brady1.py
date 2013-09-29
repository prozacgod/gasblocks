#!/usr/bin/env python
import pygame
import copy
import random
from pygame.locals import *
pygame.init()

Font = pygame.font.SysFont("monospace", 15)

size = (800, 800)
cellSize = 8
xmax = size[0]/cellSize
ymax = size[1]/cellSize

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
  def __init__(self,typ,pres):
    self.t = typ
    self.p = pres

  def getColor(self):
    if self.t == 0:
	return (0,0,0)
    if self.t == 1:
        return (0,255,0)
    colv = self.p / 8
    colv = colv % 360
    colp = pygame.Color(0,0,0,0)
    colp.hsva = (colv,99,50 if self.t==3 else 99,99)
    return colp

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


#gas-air interface
def baif(x,y,arr):
	if x < 1 or y < 1 or x > xmax-1 or y > ymax-1:
		return
	if not arr[x][y].t == 2:
		return
	if arr[x-1][y].t == 0:
		return True
	if arr[x+1][y].t == 0:
		return True
	if arr[x][y+1].t == 0:
		return True
	if arr[x][y-1].t == 0:
		return True

#Solid-gas interface
def bgif(x,y,arr):
	if x < 1 or y < 1 or x > xmax-1 or y > ymax-1:
		return
	if not arr[x][y].t == 2:
		return
	if arr[x-1][y].t == 3:
		return True
	if arr[x+1][y].t == 3:
		return True
	if arr[x][y+1].t == 3:
		return True
	if arr[x][y-1].t == 3:
		return True

def ccfoam(x,y,arr,arrnew):
	if x < 1 or y < 1 or x > xmax-1 or y > ymax-1:
		return
	gv = arr[x][y].p
	if not arr[x][y].t==2:
		return
	if gv < 2:
		arrnew[x][y].t=3
		#arr[x][y].t=3
		return
	arrnew[x][y].p=arr[x][y].p+random.randint(gv/3,gv/2)
	validpos = []
	#isfreeze=False
	
	if arr[x-1][y].t == 0 or arr[x-1][y].t == 2:
		validpos.append((x-1,y))
	if arr[x+1][y].t == 0 or arr[x+1][y].t == 2:
		validpos.append((x+1,y))
	if arr[x][y+1].t == 0 or arr[x][y+1].t == 2:
		validpos.append((x,y+1))
	if arr[x][y-1].t == 0 or arr[x][y-1].t == 2:
		validpos.append((x,y-1))
	
	print validpos
	if len(validpos) == 0:
		return
	dv = int((gv/len(validpos))*(len(validpos)/2))
	for bl in validpos:
		arrnew[bl[0]][bl[1]].p = arr[bl[0]][bl[1]].p + dv - random.randint(0,dv/4)
		arrnew[bl[0]][bl[1]].t=2

	
def cycle(arr):
	arrnew = copy.deepcopy(arr)
	for x in range(len(arr)):
		for y in range(len(arr[x])):
			if(baif(x,y,arr)):
				print "blockair if "+str((x,y))
				ccfoam(x,y,arr,arrnew)
			elif(bgif(x,y,arr)):
				print "blockgas if "+str((x,y))
				arrnew[x][y].t=3
				#arr[x][y].t=3

	arr = copy.deepcopy(arrnew)
	return arr

class GameGrid:
  def __init__(self, w, h):
    self.cells = [[GasCell(0,0) for x in range(w)] for y in range(h)]
      
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
    self.cells = cycle(self.cells)
    pass
      
def subdes(x,y,arr):
	if x < 1 or y < 1 or x > xmax-1 or y > ymax-1:
		return
	if arr[x,y].t==3:
		arr[x,y].t=2
		arr[x,y].p=(arr[x,y].p+5)*32

def destroy(x,y,arr):
	if x < 1 or y < 1 or x > xmax-1 or y > ymax-1:
		return
	arr[x,y].t=0
	for a in range(x-2,x+2):
		for b in range(y-2,y+2):
			subdes(a,b,arr)

def processEvent(gg, event):
  global running
  if event.type == QUIT:
    running = False
      
  elif event.type == KEYDOWN:
    if event.key == K_ESCAPE:
      running = False
    if event.key == K_SPACE:
      gg.update();
    if event.key == K_x:
      x = pygame.mouse.get_pos()[0]/cellSize
      y = pygame.mouse.get_pos()[1]/cellSize
      destroy(x,y,gg)
    if event.key == K_r:
      gg.cells = [[GasCell(0,0) for x in range(xmax)] for y in range(ymax)]
  elif event.type == MOUSEBUTTONDOWN:
    x = event.pos[0]/cellSize
    y = event.pos[1]/cellSize
    cell = gg[x,y]
    if event.button == 1:
      gg[x,y].t=1
    elif event.button == 3:
      gg[x,y] = GasCell(2,5000)
      
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
