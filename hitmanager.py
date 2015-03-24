# *** Imports ***
import pygame, sys, os, time
from pygame.locals import *
from gameboard import GameBoard
from gamestate import GameState
from shipmanager import ShipManager

class Peg:

	#Radius of the pegs
	size = 5

	def __init__(self, surface, boardSide, x, y):
		self.surface = surface
		self.boardSide = boardSide
		self.x = x
		self.y = y
		self.isSet = False

	#Set the peg and indicate the color to use (if it's a hit or not).
	def setPeg(self, color):
		self.isSet = True
		self.color = color

	#Renders the peg if it has been set.
	def render(self):
		if (self.isSet):
			#Get the yOffset based on which side of the board the peg is on.
			yOffset = GameBoard.yOffset_bottom if (self.boardSide == GameBoard.BOTTOM) else GameBoard.yOffset_top

			#Get the actual x and y values in pixels.
			dx = (self.x*GameBoard.tileSize) + (GameBoard.tileSize / 2) + GameBoard.xOffset
			dy = (self.y*GameBoard.tileSize) + (GameBoard.tileSize / 2) + yOffset

			#Render the shadow
			pygame.draw.circle(self.surface, pygame.Color(0,0,0,255), [dx+2, dy+2], Peg.size)
			#Render the peg.
			pygame.draw.circle(self.surface, pygame.Color(self.color), [dx, dy], Peg.size)


#Manages the hit spots on the boards. 
class HitManager:

	def __init__(self, surface):
		self.surface = surface

		#Create 2D lists for the top and bottom game boards.
		self.pegList_top = self._getBlankList(GameBoard.TOP)
		self.pegList_bottom = self._getBlankList(GameBoard.BOTTOM)

	def _getBlankList(self, boardSide):
		l = []

		for x in range(GameBoard.boardSize):
			l.append([])
			for y in range(GameBoard.boardSize):
				l[x].append(Peg(self.surface, boardSide, x, y))

		return l

	def setPeg(self, x, y, pegList, shipMan):
		#Check if any ships were hit
		hitShip = shipMan.shipIntersectsPoint([x, y])
		color = "red" if (hitShip) else "white"

		pegList[x][y].setPeg(color)

		return hitShip

	def checkSunkShip(self, ship):
		for loc in ship.getOccupiedTiles():
			if (not self.pegList_top[loc[0]][loc[1]].isSet):
				return False
		return True

	def checkGameOver(self, shipList):
		for ship in shipList:
			if (not ship.isSunk):
				return False
		return True

	def update(self, main):

		if (main.gameState == GameState.Attacking):

			#Mouse x,y tile coords.
			mx, my = main.inp.getMouseGridPos()

			if (main.gameBoard.topGridRectangle().collidepoint(main.inp.mousePos)):
				if (not self.pegList_top[mx][my].isSet):
					#Highlight tile on mouseover on top grid, only if no peg is on the tile.
					main.gameBoard.setTileToUpdate([main.inp.getMouseGridPos()], GameBoard.TOP)

					#If not peg is on tile, and mouse is clicked, set a new peg on the tile.
					if (main.inp.mouseClicked[0] == 1 and main.inp.prevMouseClicked[0] != 1):
						# color = "red" if (main.opponent.shipMan.shipIntersectsPoint([main.inp.getMouseGridPos()[0], main.inp.getMouseGridPos()[1]])) else "white"
						# self.pegList_top[main.inp.getMouseGridPos()[0]][main.inp.getMouseGridPos()[1]].setPeg(color)

						ship = self.setPeg(main.inp.getMouseGridPos()[0], main.inp.getMouseGridPos()[1], self.pegList_top, main.opponent.shipMan)

						#Ship was hit.
						if (ship):
							main.sound.play("hit")
							if (self.checkSunkShip(ship)):
								ship.isSunk = True
								main.opponent.shipsToDraw.append(ship)
								main.prevGameState = GameState.Defending
								main.gameState = GameState.ShipWasSunk
								main.helpergui.shipSunk(ship.shipName, 0)
						#Ship was not hit.
						else:
							main.sound.play("missed_hit")

						main.gameState = GameState.Defending

		elif (main.gameState == GameState.Defending):
			#Give the opponent some time to move instead of instantaneously.
			time.sleep(2)
			#Opponent's attack method.
			main.opponent.attack(main)

		if (main.gameState == GameState.Attacking or main.gameState == GameState.Defending):
			if (self.checkGameOver(main.shipMan.shipList)):
				main.gameState = GameState.GameOver
				main.helpergui.whoWon = 1
			elif (self.checkGameOver(main.opponent.shipMan.shipList)):
				main.gameState = GameState.GameOver
				main.helpergui.whoWon = 0


	def render(self):
		for x in range(len(self.pegList_top)):
			for y in range(len(self.pegList_top[0])):
				self.pegList_top[x][y].render()
				self.pegList_bottom[x][y].render()