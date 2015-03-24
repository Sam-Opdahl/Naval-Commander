# *** Imports ***
import pygame, sys, os
import random as rand
from pygame.locals import *
from gameboard import GameBoard
from shipmanager import ShipManager
from gamestate import GameState

class OpponentType:

	AI = 0
	NetworkedPlayer = 1

class Direction:

	Up = [0, 1]
	Right = [1, 0]
	Down = [0, -1]
	Left = [-1, 0]

	dirList = [Up, Right, Down, Left]

class Opponent:

	def __init__(self, surface, oppType):
		self.oppType = oppType
		#Create a shipmanager for the top board.
		self.shipMan = ShipManager(surface, GameBoard.TOP)

		#self.attack = the attack method used by the opponent.
		if (oppType == OpponentType.AI):

			#Holds a list of the ships that will be drawn (sunken ships).
			self.shipsToDraw = []

			#Holds lists of coords where each ship has been hit.
			self.shipHitDict = {}
			for name in ShipManager.shipName:
				d = {name: []}
				self.shipHitDict.update(d)

			#Contains the ship that is the current target
			self.curTargetShip = None
			#Contains a list of all ships that have been hit and are secondary targets
			self.targetShips = []
			#contains the coords of the pivot point of a ship that was hit.
			self.pivotPos = None
			#Contains the coords of current position that is being checked
			self.posToCheck = None
			#Contains the current direction we are traversing on the grid from the pivot point.
			self.trackDirection = None
			#Contains a list of the directions that were already check for the current target ship.
			self.CheckedDirections = []

			#Generate random ship positions for the AI.
			self.generateRandomShipPositions()
			#Set the attack method to the AI attack method.
			self.attack = self.AI_attack
		else:
			self.attack = self.network_attack
			self.client = GameClient()

	#Use if the opponent type is AI.
	#This method randomizes the ship starting positions in the shipmanager
	def generateRandomShipPositions(self): 
		for ship in self.shipMan.shipList:
			#50/50 chance of the ship being horizontal/vertical.
			if (rand.randint(1, 10) <= 5):
				ship.rotate()

			#Generate random x and y coords
			ship.x = rand.randint(0, (GameBoard.boardSize-1) - ship.unitLength()[0])
			ship.y = rand.randint(0, (GameBoard.boardSize-1) - ship.unitLength()[1])

		#Go through the ship list again and make sure no ships are intersecting.
		#If any ships are intersecting, give it new x,y coords until no intersects are present.
		#A seperate loop is used to make sure ship locations are completely random.
		#If it would've been checked in the above loop, the top left corner would have a higher chance of being unused, 
		#since that is where the ships are initially located.
		for ship in self.shipMan.shipList:
			while (self.shipMan.shipIntersections(ship)):
				ship.x = rand.randint(0, (GameBoard.boardSize-1) - ship.unitLength()[0])
				ship.y = rand.randint(0, (GameBoard.boardSize-1) - ship.unitLength()[1])

	def AI_attack(self, main):

		#If we have a target ship
		if (self.curTargetShip):
			#Keep looping until a peg has been set on the grid.
			while (True):

				#Get the x and y coords based on the current trackDirection we are going.
				x = self.posToCheck[0] + Direction.dirList[self.trackDirection][0]
				y = self.posToCheck[1] + Direction.dirList[self.trackDirection][1]
				self.posToCheck = [x, y]

				#If the position to check is within the board grid and the grid point hasn't already been hit.
				if ((x >= 0 and x < GameBoard.boardSize-1) and (y >= 0 and y < GameBoard.boardSize-1) and (not main.hitMan.pegList_bottom[x][y].isSet)):
					#Set the peg on the bottom list and based on the player's list of ships.
					ship = main.hitMan.setPeg(x, y, main.hitMan.pegList_bottom, main.shipMan)
					#If a ship was hit...
					if (ship):
						#Add the coords to the list of hit spots for that ship.
						self.shipHitDict[ship.shipName].append([x, y])
						#If the ship that was hit isn't the current target, add it to the list of targets if it isn't already in there.
						if ((self.curTargetShip != ship) and (not ship in self.targetShips)):
							self.targetShips.append(ship)
						#Check if that hit sunk the ship.
						if (self.checkSunkShip(ship)):
							ship.isSunk = True
							main.helpergui.shipSunk(ship.shipName, 1)
							main.prevGameState = GameState.Attacking
							main.gameState = GameState.ShipWasSunk
						main.sound.play("hit")

					#If the ship wasn't hit, get a new track direction and reset back to the pivot.
					else:
						self.trackDirection = self.getRandomDirection()
						self.posToCheck = self.pivotPos
						main.sound.play("missed_hit")

					#Peg was set successfully, break out of the loop.
					break

				#If the position to check is invalid, get a new direction and reset back to the pivot point.
				else:
					self.trackDirection = self.getRandomDirection()
					self.posToCheck = self.pivotPos
		#If we don't have a current target...
		else:
			while (True):
				#Generate a random position to attack
				hx = rand.randint(0, GameBoard.boardSize-2)
				hy = rand.randint(0, GameBoard.boardSize-2)

				#If the peg does not exist yet, set it and break
				if (not main.hitMan.pegList_bottom[hx][hy].isSet):
					ship = main.hitMan.setPeg(hx, hy, main.hitMan.pegList_bottom, main.shipMan)
					break

			#If we hit a ship, set it as the target
			if (ship):
				self.curTargetShip = ship
				self.trackDirection = self.getRandomDirection()
				self.shipHitDict[ship.shipName].append([hx, hy])
				self.pivotPos = [hx, hy]
				self.posToCheck = [hx, hy]
				main.sound.play("hit")
			else:
				main.sound.play("missed_hit")

		if (main.gameState != GameState.ShipWasSunk):
			main.gameState = GameState.Attacking

	def checkSunkShip(self, shipToCheck):
		#Check if current ship is sunk by checking all of the ship's positions againt its hit list.
		for loc in shipToCheck.getOccupiedTiles():
			#If the ship hasn't been sunk, exit the method.
			if (not loc in self.shipHitDict[shipToCheck.shipName]):
				return False
		
		#If the sunken ship is the target...
		if (shipToCheck == self.curTargetShip):
			#reset the list of checked directions.
			self.CheckedDirections = []

			#If there are any other target ships...
			if (len(self.targetShips) > 0):
				#set the next one on the list as the current target and remove from the list.
				self.curTargetShip = self.targetShips.pop(0)
				#Set the pivot position as the spot that has been hit on the ship.
				self.pivotPos = self.shipHitDict[self.curTargetShip.shipName][0]
				self.posToCheck = self.pivotPos
				self.trackDirection = self.getRandomDirection()
			#If there are no targets left on the list, continue checking random positions.
			else:
				self.curTargetShip = None
		#If the sunken ship isn't the target...
		else:
			#Remove the sunken ship from the list of targets.
			for i in range(len(self.targetShips)):
				if (self.targetShips[i] == shipToCheck):
					self.targetShips.pop(i)
					break

		return True



	#Returns a random direction that hasn't already been checked.
	def getRandomDirection(self):
		while (True):
			#Get a random direction.
			d = rand.randint(0, len(Direction.dirList)-1)
			#If the direction has already been checked, get a new random direction.
			if (not d in self.CheckedDirections):
				break
		#Add the direction to the list of checked directions.
		self.CheckedDirections.append(d)
		return d

	def network_attack(self, hitMan):
		pass

	def renderShips(self, main):
		#self.shipMan.renderShips()

		if (self.oppType == OpponentType.AI):
			if (main.gameState != GameState.GameOver):
				shipList = self.shipsToDraw
			else:
				shipList = self.shipMan.shipList

			for ship in shipList:
				ship.render()