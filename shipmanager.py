# *** Imports ***
import pygame, sys, os
from pygame.locals import *
from ship import Ship
from gamestate import GameState
from gameboard import GameBoard


################################################################################
#
#	shipmamanger.py
#
#	class ShipManager - 
#		Manages ships for the indicated board. 
#		Updates ship positions, draws ships.
#		Contains methods to find ships on the board.
#
################################################################################


class ShipManager:

	#Total number of ships.
	totalShips = 5
	#List of each ship name.
	shipName = ["Patrol Boat", "Submarine", "Destroyer", "Battleship", "Aircraft Carrier"]

	#boardside indicates which side of the board the ships will be managed on
	def __init__(self, surface, boardSide):
		self.surface = surface
		self.boardSide = boardSide
		self.grabbedShip = None
		self.loadShips()

	def loadShips(self):
		self.shipList = []

		for i in range(ShipManager.totalShips):
			#Get the ship to load's file name.
			path = "image\\ship" + str(i+1) + ".png"

			#Create a new ship class and append it to the list of ships.
			self.shipList.append(Ship(self.surface, path, ShipManager.shipName[i], 0, i, self.boardSide))

	#Check the "toCheck" ship and see if it intersects any other ships in shipList
	def shipIntersections(self, toCheck):
		for ship in self.shipList:
			if (toCheck.shipName == ship.shipName):
				continue
			if (toCheck.getCollisionRect().colliderect(ship.getCollisionRect())):
				return True

		return False

	#Check if a ship intersects a point [x, y].
	def shipIntersectsPoint(self, point):
		for ship in self.shipList:
			if (point in ship.getOccupiedTiles()):
				return ship
		return None


	#Highlights the mouse position on the bottom board when placing ships.
	def highlightMousePos(self, inp, gameBoard):
		#If mouse is visible, highlight the tile the mouse is hovering over. 
		if (inp.mouseVisible):
			if (gameBoard.bottomGridRectangle().collidepoint(inp.mousePos)):
				for ship in self.shipList:
					if (inp.getMouseGridPos() in ship.getOccupiedTiles()):
						#If mouse is hovering a ship, highlight entire ship
						gameBoard.setTileToUpdate(ship.getOccupiedTiles(), GameBoard.BOTTOM)
						return
				#If mouse is hovering a single tile, highlight the tile
				gameBoard.setTileToUpdate([inp.getMouseGridPos()], GameBoard.BOTTOM)


	def update(self, state, inp, gameBoard):

		#If we are currently in the ship placement process
		if (state == GameState.ShipPlacement):

			self.highlightMousePos(inp, gameBoard)

			#Check if mouse has been clicked
			if (inp.mouseClicked[0] == 1 and inp.prevMouseClicked[0] != 1):
				#make sure the user isn't holding a ship already
				if (not self.grabbedShip):
					for ship in self.shipList:
						#Check for collision between mouse and the ships
						if (ship.getCollisionRect().collidepoint(pygame.mouse.get_pos())):
							#set the selected ship as the grabbed ship.
							self.grabbedShip = ship
							inp.setMouseVisible(False)
							return

			keyState, prevKeyState = inp.keyState, inp.prevKeyState

			#If a ship is currently grabbed, keyboard for input
			if (self.grabbedShip):

				#If the grabbed ship is intersecting another ship, make the highlight color red because player cannot place ship there.
				color = "white" if (not self.shipIntersections(self.grabbedShip)) else "red"
				#Highlight the tiles the grabbed ship is currently on.
				gameBoard.setTileToUpdate(self.grabbedShip.getOccupiedTiles(), GameBoard.BOTTOM, color)

				#Check if left mosue button was clicked, if so attempt to place ship
				if (inp.mouseClicked[0] == 1 and inp.prevMouseClicked[0] != 1):
					#If the ship is on another ship, don't allow it to be placed.
					if (color != "red"):
						self.grabbedShip = None
						inp.setMouseVisible(True)
						return
				#Check if rotate key was pressed, if so rotate ship (currently right mouse button)
				elif (inp.mouseClicked[2] == 1 and inp.prevMouseClicked[2] != 1):
					self.grabbedShip.rotate()

				#set the ship's x,y coords to follow the mouse
				self.grabbedShip.x, self.grabbedShip.y = inp.getMouseGridPos(GameBoard.yOffset_bottom)

				#Check the mouse pos and ship pos, make sure they stay within the board's bounds
				if (self.grabbedShip.y < 0):
					self.grabbedShip.y = 0
					pygame.mouse.set_pos([inp.mousePos[0], GameBoard.yOffset_bottom])
				if (self.grabbedShip.x < 0):
					self.grabbedShip.x  = 0
					pygame.mouse.set_pos([GameBoard.xOffset, inp.mousePos[1]])
				if (self.grabbedShip.y + self.grabbedShip.unitLength()[1] > GameBoard.boardSize-1):
					self.grabbedShip.y = GameBoard.boardSize-1 - self.grabbedShip.unitLength()[1]
					pygame.mouse.set_pos([inp.mousePos[0], GameBoard.yOffset_bottom + ((GameBoard.boardSize-1 - self.grabbedShip.unitLength()[1]) * GameBoard.tileSize)])
				if (self.grabbedShip.x + self.grabbedShip.unitLength()[0] > GameBoard.boardSize-1):
					self.grabbedShip.x = GameBoard.boardSize-1 - self.grabbedShip.unitLength()[0]
					pygame.mouse.set_pos([GameBoard.xOffset + ((GameBoard.boardSize-1 - self.grabbedShip.unitLength()[0]) * GameBoard.tileSize), inp.mousePos[1]])

	#Render all the ships in shipList.
	def renderShips(self):
		for s in self.shipList:
			s.render()