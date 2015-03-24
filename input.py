# *** Imports ***
import pygame, sys, os
from pygame.locals import *
from gameboard import GameBoard

#Manages input object and contains helpful input methods
class Input:

	def __init__(self):
		#Hold the current and previous mouse positions
		self.prevMousePos = None
		self.mousePos = pygame.mouse.get_pos()

		#Hold the current and previous key pressed
		self.prevKeyState = None
		self.keyState = pygame.key.get_pressed()

		#Hold the mouse clicking states
		self.prevMouseClicked = None
		self.mouseClicked = pygame.mouse.get_pressed()

		#Do not set directly, use setMouseVisible(). only get value from variable.
		self.mouseVisible = True

	#Get the position of the mouse in tiles units. returns [x, y]
	#Use yOffset to specify a specific side of the board, otherwise it will auto detect.
	def getMouseGridPos(self, yOffset=None):
		if (not yOffset):
			yOffset = GameBoard.yOffset_bottom if (self.mousePos[1] >= GameBoard.yOffset_bottom) else GameBoard.yOffset_top

		return [(self.mousePos[0] - GameBoard.xOffset) // GameBoard.tileSize, (self.mousePos[1] - yOffset) // GameBoard.tileSize]

	#Set mouse visibility
	def setMouseVisible(self, value):
		pygame.mouse.set_visible(value)
		self.mouseVisible = value

	#Check for exit and other events
	def checkEvents(self):
		for event in pygame.event.get():
			if (event.type == QUIT):
				sys.exit(0)

	#Update all states of the keyboard and mouse
	def update(self):

		self.checkEvents()

		self.prevMousePos = self.mousePos
		self.mousePos = pygame.mouse.get_pos()

		self.prevMouseClicked = self.mouseClicked
		self.mouseClicked = pygame.mouse.get_pressed()

		self.prevKeyState = self.keyState
		self.keyState = pygame.key.get_pressed()

		#Check if the esc key was pressed and create a quit event to exit the game
		#Pressing the close button automatically creates a quit event.
		if (self.keyState[K_ESCAPE]):
			pygame.event.post(pygame.event.Event(QUIT))