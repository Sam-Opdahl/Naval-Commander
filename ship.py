# *** Imports ***
import pygame, sys, os
from pygame.locals import *
from gameboard import GameBoard

#Class that represents a single ship
class Ship:

	#Constant to indicate which way the ship is facing
	HORIZONTAL, VERTICAL = 0, 1

	def __init__(self, surface, spritePath, shipName, x, y, boardSide):
		self.x, self.y = x, y
		self.surface = surface
		self.shipName = shipName
		self.boardSide = boardSide
		self.direction = Ship.HORIZONTAL
		self.isSunk = False

		self.sprite = []
		#sprite[0] = original horizontal sprite
		self.sprite.append(pygame.transform.rotate(pygame.image.load(spritePath).convert(), 180))
		#sprite[1] = rotated vertical sprite
		self.sprite.append(pygame.transform.rotate(self.sprite[Ship.HORIZONTAL], 270))

		self._maxLength = max(self.unitLength())

	#Rotates the ship - use when placing ships initially
	def rotate(self):
		#If ship is horizontal, make it vertival
		if (self.direction == Ship.HORIZONTAL):
			self.direction = Ship.VERTICAL
			#Check if the ship is out of the game board bounds, if it is put it back inside
			if (self.y + self.unitLength()[1] > GameBoard.boardSize-1):
				self.y -= (self.y + self.unitLength()[1]) - (GameBoard.boardSize-1)
		#If ship is vertical, make it horizontal
		else:
			self.direction = Ship.HORIZONTAL
			#Check if the ship is out of the game board bounds, if it is put it back inside
			if (self.x + self.unitLength()[0] > GameBoard.boardSize-1):
				self.x -= (self.x + self.unitLength()[0]) - (GameBoard.boardSize-1)

	#return collision rectangle for the ship
	def getCollisionRect(self):
		x, y = self.getRealCoords()
		width = self.sprite[self.direction].get_width()
		height = self.sprite[self.direction].get_height()

		return pygame.Rect(x, y, width, height)

	#Gets the actual x,y coords of the ship in pixels
	def getRealCoords(self):
		yOffset = GameBoard.yOffset_bottom if (self.boardSide == GameBoard.BOTTOM) else GameBoard.yOffset_top
		return [(self.x * GameBoard.tileSize) + GameBoard.xOffset + 1, (self.y * GameBoard.tileSize) + yOffset + 1]

	#Gets the unitWidth and unitHeight refers to how many spaces (tiles) the ship is width/height-wise
	def unitLength(self):
		unitHeight = self.sprite[self.direction].get_height() / GameBoard.tileSize
		unitWidth = self.sprite[self.direction].get_width() / GameBoard.tileSize
		return [unitWidth, unitHeight]

	#Gets a list of the tiles that this ship is currently on.
	def getOccupiedTiles(self):
		x, y = self.x, self.y
		#Set initial x,y coord
		tileList = [[x, y]]

		for i in range(self._maxLength - 1):
			#If ship is horizontal, we simply need to move the x coord over by 1
			if (self.direction == Ship.HORIZONTAL):
				x += 1
				tileList.append([x, y])
			#Same for being vertical and moving the y coord.
			else:
				y += 1
				tileList.append([x, y])

		return tileList

	#Render the ship based on it's direction and coords.
	def render(self):
		self.surface.blit(self.sprite[self.direction], self.getRealCoords())