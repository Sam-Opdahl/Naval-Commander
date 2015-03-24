"""

A battleship style game created using pygame.

The opponent uses a simple AI where it randomly guesses positions on the board,
but it is smart enough to follow up and check position around a spot where it hit a ship.

Completed 12/11/12

"""


# *** Imports ***
import pygame, sys, os
from pygame.locals import *
from input import Input
from gameboard import GameBoard
from ship import Ship
from shipmanager import ShipManager
from gamestate import GameState
from hitmanager import HitManager
from opponent import *
from helpergui import Helpergui
from sound import Sound

class Main:

	#Height and width of the game screen
	screenWidth = 650
	screenHeight = 750

	#clock to display and limit fps
	Clock = pygame.time.Clock()

	def __init__(self):
		#init pygame objects
		pygame.init()
		self.window = pygame.display.set_mode([self.screenWidth, self.screenHeight])
		self.screen = pygame.display.get_surface()

		self.gameState = GameState.ShipPlacement
		self.initGameObjects()

	def initGameObjects(self):
		self.prevGameState = self.gameState
		self.inp = Input()
		self.gameBoard = GameBoard(self)
		self.shipMan = ShipManager(self.screen, GameBoard.BOTTOM)
		self.hitMan = HitManager(self.screen)
		self.opponent = Opponent(self.screen, OpponentType.AI)
		self.helpergui = Helpergui(self)
		self.sound = Sound(self.screen)

	#Starts a new game
	def startNewGame(self):
		#Reset gamestates
		self.gameState = GameState.ShipPlacement
		self.prevGameState = self.gameState

		#delete and create new instances of pertinent classes.
		del self.shipMan
		self.shipMan = ShipManager(self.screen, GameBoard.BOTTOM)
		del self.hitMan
		self.hitMan = HitManager(self.screen)
		del self.opponent
		self.opponent = Opponent(self.screen, OpponentType.AI)

	#Main loop for the game
	def mainloop(self):

		while (True):
			#Set max FPS
			self.Clock.tick(250)
			#Window Title
			pygame.display.set_caption("Naval Commander - FPS: %.2f" % (self.Clock.get_fps()))

			self.updateAll()
			self.renderAll()

	#Run class update methods
	def updateAll(self):

		#no matter what state, always update the input.
		self.inp.update()

		#If we are currently playing the game update it.
		if (self.gameState >= GameState.MinPlayingState):

			self.hitMan.update(self)
			self.shipMan.update(self.gameState, self.inp, self.gameBoard)
			self.helpergui.update(self)
			self.sound.update(self)

	#Rune class render methods.
	def renderAll(self):
		#Render the actualy game playing objects.
		if (self.gameState >= GameState.MinPlayingState):
			self.gameBoard.renderAll(self)
			self.sound.render()
			self.opponent.renderShips(self)
			self.shipMan.renderShips()
			self.hitMan.render()
			self.helpergui.render(self)

		#draw newly rendered objects.
		pygame.display.flip()

	#Entry point of the game.
	def start(self):
		#Start the main loop.
		self.mainloop()


#Entry Point
Main().start()

