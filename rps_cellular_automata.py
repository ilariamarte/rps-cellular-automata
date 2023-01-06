#!/usr/bin/env python
import pygame
import numpy as np
from random import randint
import pygame_shaders
import os

# parameters
WINDOW_WIDTH, WINDOW_HEIGHT = 800,500
WINDOW_SURFACE = pygame.OPENGL | pygame.DOUBLEBUF | pygame.HWSURFACE # Create an opengl renderable display

BLACK     = (   0,   0,   0 )
DARK_BLUE = (   3,   5,  54 )
WHITE     = ( 255, 255, 255 )

COLOR1    = "coral"
COLOR2    = "blue"
COLOR3    = "cyan"

dirname = os.path.dirname(__file__) # directory of the file in use
vertex_dir = os.path.join(dirname, "shader/vertex.txt")
fragment_dir = os.path.join(dirname, "shader/default_frag.txt")

start_x, start_y = 50,50
n_tile_x, n_tile_y = 80,80
tile_x, tile_y = 5,5
start_x, start_y = (WINDOW_WIDTH-n_tile_x*tile_x)/2, (WINDOW_HEIGHT-n_tile_y*tile_y)/2


class Board:
	def __init__(self, start_x, start_y, n_tile_x, n_tile_y, tile_x, tile_y):
		self.start_x, self.start_y = start_x, start_y
		self.n_tile_x, self.n_tile_y = n_tile_x, n_tile_y
		self.tile_x, self.tile_y = tile_x, tile_y
		self.color = np.full((n_tile_x, n_tile_y), "black")
		self.gradient = np.full((n_tile_x, n_tile_y), 0)
		self.updated_color = "black"
		self.last_col = COLOR2
		self.mux = 0
	
	def draw_board(self, screen):
		for i in range(self.n_tile_x):
			for j in range(self.n_tile_y):
				ii = self.start_x + i*self.tile_x
				jj = self.start_y + j*self.tile_y
				pygame.draw.rect(screen, self.color[i,j], pygame.Rect(ii, jj, self.tile_x, self.tile_y))
	
	def eating_function(self, screen, x,y, col_eater, col_food):
		"""checks if col is near, if so, eats it"""
		x1,x2,y1,y2 = -1,1,-1,1
		if x == 0: x1 = 0
		if y == 0: y1 = 0
		if x == self.n_tile_x-1: x2 = 0
		if y == self.n_tile_y-1: y2 = 0
		for addx in range(x1,x2):
			for addy in range(y1,y2):
				i,j = x+addx,y+addy
				if self.color[i,j] == col_food:
					self.color[i,j] = col_eater
					self.gradient[i,j] = 10

	def eating_rule(self, screen, x,y, col):
		if col == COLOR1:
			self.eating_function(screen, x,y, COLOR1,COLOR2)
		elif col == COLOR2:
			self.eating_function(screen, x,y, COLOR2,COLOR3)
		elif col == COLOR3:
			self.eating_function(screen, x,y, COLOR3,COLOR1)

	def update(self, screen):
		for x in range(self.n_tile_x):
			for y in range(self.n_tile_y):
				if self.color[x,y] != "black" and self.gradient[x,y] > 1:
					addx, addy = 0, 0
					x1,x2,y1,y2 = -1,1,-1,1
					if x == 0: x1 = 0
					if y == 0: y1 = 0
					if x == self.n_tile_x-1: x2 = 0
					if y == self.n_tile_y-1: y2 = 0
					while (addx == 0 and addy == 0) or (x+addx >= n_tile_x or y+addy >= n_tile_y or x+addx < 0 or y+addy < 0):
						addx = randint(x1,x2)
						addy = randint(y1,y2)
					i,j = x+addx,y+addy
					self.color[i,j] = self.color[x,y]
					self.gradient[i,j] = self.gradient[x,y]-1
				if self.color[x,y] != "black":
					self.eating_rule(screen, x,y, self.color[x,y])
	
	def check_hit(self, x, y):
		"""check if x,y are inside the Board"""
		max_x = self.start_x + self.n_tile_x * self.tile_x
		max_y = self.start_y + self.n_tile_y * self.tile_y
		if x > self.start_x and x < max_x and y > self.start_y and y < max_y:
			return True
		else:
			return False
	
	def interface(self, screen, mouse_down):
		"""mouse click on board"""
		x,y = pygame.mouse.get_pos()
		if mouse_down and self.check_hit(x,y): # left click
			self.mux = 1
			for i in range(self.n_tile_x):
				for j in range(self.n_tile_y):
					ii = self.start_x + i*self.tile_x
					jj = self.start_y + j*self.tile_y
					if x > ii and x < ii + self.tile_x and y > jj and y < jj + self.tile_y:
						if self.last_col == COLOR1:
							self.color[i,j] = COLOR3
						elif self.last_col == COLOR2:
							self.color[i,j] = COLOR1
						else:
							self.color[i,j] = COLOR2
						self.updated_color = self.color[i,j]
						self.gradient[i,j] = 10
						# pygame.draw.rect(screen, self.color[i,j], pygame.Rect(ii+1, jj+1, self.tile_x-2, self.tile_y-2))
		if self.mux and not mouse_down: # release left click
			self.last_col = self.updated_color
			self.mux = 0
	
	def reset(self):
		self.color = np.full((n_tile_x, n_tile_y), "black")
		self.gradient = np.full((n_tile_x, n_tile_y), 0)

def init():
	pygame.init()
	pygame.display.set_caption("RPS Cellular Automata")
	window = pygame.display.set_mode( ( WINDOW_WIDTH, WINDOW_HEIGHT ), WINDOW_SURFACE )
	canvas = pygame.Surface( ( WINDOW_WIDTH, WINDOW_HEIGHT ) )
	canvas.fill( BLACK )
	canvas.set_colorkey( DARK_BLUE ) # Make all black on the display transparent
	shader = pygame_shaders.Shader(size=(WINDOW_WIDTH, WINDOW_HEIGHT), display=(WINDOW_WIDTH, WINDOW_HEIGHT), 
									pos=(0, 0), vertex_path= vertex_dir, 
									fragment_path=fragment_dir) # Load your shader
	clock = pygame.time.Clock()
	b = Board(start_x, start_y, n_tile_x, n_tile_y, tile_x, tile_y)
	return window, canvas, shader, clock, b

if __name__ == "__main__":
	loop = True
	mouse_down = False
	last_col = COLOR2
	window, canvas, shader, clock, b = init()
	while loop:
		for event in pygame.event.get():
			if event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_ESCAPE]:
				loop = False
			elif ( event.type == pygame.MOUSEBUTTONDOWN ):
				mouse_down = True
			elif ( event.type == pygame.MOUSEBUTTONUP ):
				mouse_down = False
		
		pygame_shaders.clear(BLACK) # Fill with the color you would like in the background
		canvas.fill(DARK_BLUE) # Fill with the color you set in the colorkey

		b.interface(canvas,mouse_down)
		b.update(canvas)
		b.draw_board(canvas)

		if pygame.key.get_pressed()[pygame.K_SPACE]:
			b.reset()
		
		shader.render(canvas) # Render the display onto the OpenGL display with the shaders
		pygame.display.flip()

pygame.quit()
