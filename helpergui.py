# *** Imports ***
import pygame, sys, os
from pygame.locals import *
from gamestate import GameState
from gameboard import GameBoard



class Button:	

	#Pad globals contain the padding between the text and the border of the button.
	wPad, hPad = 10, 5

	#Color globals for the buttons.
	textColor = "black"
	normalColor = "grey"
	highlightColor = "darkgrey"

	def __init__(self, surface, text, helperRect, event):
		self.surface = surface
		self.text = text
		self.color = Button.normalColor
		#Contains the method to run when the button is clicked.
		self.event = event

		#Set up font
		self.font = pygame.font.SysFont("Arial", 12)
		self.text = self.font.render(text, 1, pygame.Color("black"))

		#Calculate for the button and text
		width = self.font.size(text)[0] + Button.wPad
		height = self.font.size(text)[1] + Button.hPad
		x = helperRect[0] + (helperRect[2]/2) - (width/2)
		y = 600

		#Position of the text of the button.
		self.textPos = [x + (Button.wPad/2), y + (Button.hPad/2)]
		#Positiong of the button itself.
		self.buttonRect = pygame.Rect(x, y, width, height)


	def update(self, main):

		#If either the enter or space keys were hit, run the event.
		if ((main.inp.keyState[K_RETURN] and not main.inp.prevKeyState[K_RETURN]) or 
			(main.inp.keyState[K_SPACE] and not main.inp.prevKeyState[K_SPACE])):
			self.event(main)
			return

		#Check for mouse collision
		if (self.buttonRect.collidepoint(pygame.mouse.get_pos())):
			#Highlight button if mouse is over it.
			self.color = Button.highlightColor
			#If mosue button is clicked, run the event.
			if (main.inp.mouseClicked[0] == 1 and main.inp.prevMouseClicked[0] != 1):
				self.event(main)
		else:
			#If mosue isn't over button, no highlight.
			self.color = Button.normalColor

	#Render button and text.
	def render(self):
		pygame.draw.rect(self.surface, pygame.Color(self.color), self.buttonRect)
		self.surface.blit(self.text, self.textPos)


class Helpergui:

	def __init__(self, main):
		self.surface = main.screen
		self._prevGameState = main.gameState
		self.whoWon = None

		#Set up the rectangle for gui box and the shadow.
		x, y, w, h = 400, 200, 225, 450
		self._helperRect = pygame.Rect(x, y, w, h)
		self._helpRectShadow = pygame.Rect(x+5, y+5, w, h)

		self.startButton = Button(self.surface, "Declare War!", self._helperRect, self._decWarBtnEvent)
		self.gameOverButton = Button(self.surface, "Start New Game", self._helperRect, self._gameOverEvent)
		self.continueButton = Button(self.surface, "Continue", self._helperRect, self._continueEvent)

	# --------- Events ----------

	def _decWarBtnEvent(self, main):
		main.gameState = GameState.Attacking

	def _gameOverEvent(self, main):
		main.startNewGame()

	def _continueEvent(self, main):
		main.gameState = main.prevGameState


	def _renderDeclareWarButton(self):

		#render the button
		self.startButton.render()

		font = pygame.font.SysFont("Arial", 20)
		text = []
		text.append("Place your ships on")
		text.append("the bottom board and")
		text.append("declare war when")
		text.append("you're ready!")

		s = 300
		for i in range(len(text)):
			self.surface.blit(font.render(text[i], 1, pygame.Color("white")), [415, s+(20*i)])


	def renderPlayerTurn(self):
		font = pygame.font.SysFont("Arial", 20)
		text = []
		text.append("It's your Turn.")
		text.append("")
		text.append("Attack a position on")
		text.append("the top board and try")
		text.append("to sink the enemy")
		text.append("ships!")

		s = 300
		for i in range(len(text)):
			self.surface.blit(font.render(text[i], 1, pygame.Color("white")), [415, s+(20*i)])

	def renderOpponentTurn(self):
		font = pygame.font.SysFont("Arial", 20)
		text = []
		text.append("It's the opponent's")
		text.append("turn.")
		text.append("")
		text.append("Please wait while")
		text.append("your crew reloads the")
		text.append("missle launcher...")

		s = 300
		for i in range(len(text)):
			self.surface.blit(font.render(text[i], 1, pygame.Color("white")), [415, s+(20*i)])

	def renderSunkenShipMsg(self):
		font = pygame.font.SysFont("Arial", 20)
		text = []
		if (self._whichPlayer == 0):
			text.append("You sank CPU's")
			text.append(str(self._sunkenShipName) + ".")
		if (self._whichPlayer == 1):
			text.append("CPU sank your")
			text.append(str(self._sunkenShipName) + ".")

		s = 300
		for i in range(len(text)):
			self.surface.blit(font.render(text[i], 1, pygame.Color("white")), [415, s+(20*i)])

		self.continueButton.render()

	def renderGameOverMsg(self):

		self.gameOverButton.render()

		font = pygame.font.SysFont("Arial", 20)
		text = []
		text.append("Game Over!")
		text.append("")
		if (self.whoWon == 0):
			text.append("You Are Victorious!")
		else:
			text.append("You have lost the")
			text.append("battle, but the war")
			text.append("has just begun.")

		s = 300
		for i in range(len(text)):
			self.surface.blit(font.render(text[i], 1, pygame.Color("white")), [415, s+(20*i)])

	#whichPlayer: who sunk the ship. 0=human player, 1=AI player.
	def shipSunk(self, shipName, whichPlayer):
		self._sunkenShipName = shipName
		self._whichPlayer = whichPlayer

	def update(self, main): 

		#update whichever button may need to be based on the gamestate.
		if (main.gameState == GameState.ShipPlacement):
			self.startButton.update(main)
		elif (main.gameState == GameState.GameOver):
			self.gameOverButton.update(main)
		elif (main.gameState == GameState.ShipWasSunk):
			self.continueButton.update(main)


	#Render the gui, text, and buttons.
	def render(self, main):
		pygame.draw.rect(self.surface, GameBoard.menu_bg, self._helpRectShadow)
		pygame.draw.rect(self.surface, GameBoard.menu_fg, self._helperRect)

		if (main.gameState == GameState.ShipPlacement):
			self._renderDeclareWarButton()
		elif (main.gameState == GameState.Attacking):
			self.renderPlayerTurn()
		elif (main.gameState == GameState.Defending):
			self.renderOpponentTurn()
		elif (main.gameState == GameState.ShipWasSunk):
			self.renderSunkenShipMsg()
		elif (main.gameState == GameState.GameOver):
			self.renderGameOverMsg()
