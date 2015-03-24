# *** Imports ***
import pygame, sys, os
from pygame.locals import *
from gamestate import GameState


################################################################################
#
#	gameboard.py
#
#	class GameBoard - 
#		Creates, updates, and renders the game boards.
#
#
################################################################################


class GameBoard:

	#Constants to help indicate the side of the board being worked with.
	TOP, BOTTOM = 0, 1

	letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]

	#Indicates the size in pixels of the tiles on the grid
	tileSize = 30

	#Amount of tiles one each board
	boardSize = 11

	#Offset for each board
	#xOffset - centers the board on the screen
	xOffset = 50
	yOffset_top = 50
	boardGap = 10
	yOffset_bottom = yOffset_top + ((boardSize)*tileSize) + boardGap

	#Color for the grid seperators
	gridColor = pygame.Color("white")

	#Colors for the menus and game board background.
	menu_fg = pygame.Color(80,80,80,255)
	menu_bg = pygame.Color(0,0,0,255)

	#Location of the background texture for each board
	WATER_TEXTURE_LOCATION = "image\\water_texture.jpg"
	BACKGROUND_LOCATION = "image\\bg2.png"

	def __init__(self, main):
		self.surface = main.screen
		self.waterTexture = pygame.transform.scale(pygame.image.load(GameBoard.WATER_TEXTURE_LOCATION), [GameBoard.tileSize * (GameBoard.boardSize-1), GameBoard.tileSize * (GameBoard.boardSize - 1)]).convert()
		self.backgroundTexture = pygame.image.load(GameBoard.BACKGROUND_LOCATION).convert()

		self._tilesToUpdate = []
		self._tileHighlightColor = "white"
		self._sideToUpdate = GameBoard.BOTTOM

		self.createGrids()

		#When true, updates background and sets back to false.
		#Used as a simple optimization to prevent the background from redrawing every frame and causing slowdowns.
		self.updateBackground = True

	#Set the list of tiles to update, which side, and the color to use
	def setTileToUpdate(self, tileList, side, color="white"):
		self._tilesToUpdate = tileList[:]
		self._tileHighlightColor = color
		self._sideToUpdate = side


	#Calculates grid points and creates a list of points to draw the grid.
	def createGrids(self):

		#Grid for top board
		self.lineList_top = self._createGridList(GameBoard.yOffset_top)

		#Grid for bottom board
		self.linelist_bottom = self._createGridList(GameBoard.yOffset_bottom)

	#Creates a list of grid lines
	def _createGridList(self, yOffset):
		lineList = []
		boardSize = GameBoard.boardSize
		xOffset = GameBoard.xOffset
		width, height = GameBoard.tileSize, GameBoard.tileSize

		for i in range(boardSize):
			tx = (width * i) + xOffset
			ty = (height * i) + yOffset

			#vertical lines
			lineList.append([tx, yOffset])
			lineList.append([tx, (height*(boardSize-1)) + yOffset])

			#Horiztonal Lines
			lineList.append([xOffset, ty])
			lineList.append([(width*(boardSize-1)) + xOffset, ty])

		return lineList

	#Render everything except the background.
	def renderAll(self, main):

		if (self.updateBackground):
			self.renderEntireBackground(main)
			self.updateBackground = False

		self._renderTextures()
		self._renderGrids()

		if (len(self._tilesToUpdate) > 0):
			self.highlightTiles()
		self._tilesToUpdate = []

	def renderEntireBackground(self, main):
		self._renderBackgroundTexture(main)
		self._renderGameBoardBackground()
		self._renderBoardText()
		self._renderGameName()

	#Creates a tiled background based on the background image and renders it
	def _renderBackgroundTexture(self, main):
		#Hold the height/width of the background texture and screen
		tw, th = self.backgroundTexture.get_width(), self.backgroundTexture.get_height()
		sw, sh = main.screen.get_width(), main.screen.get_height()

		#Gets the amount of tiles needed to fill the screen 
		maxWidth, maxHeight = (sw // tw) + 1, (sh // th) + 1
		
		#Render the tiles
		for x in range(maxWidth):
			for y in range(maxHeight):
				self.surface.blit(self.backgroundTexture, [x * tw, y * th])

	#Draws the grey rectangle behind the grids as well as the shadow.
	def _renderGameBoardBackground(self):
		x, y = GameBoard.xOffset - GameBoard.tileSize, GameBoard.yOffset_top - GameBoard.tileSize
		w, h = GameBoard.xOffset + ((GameBoard.boardSize-1) * GameBoard.tileSize), GameBoard.yOffset_top + ((GameBoard.boardSize) * GameBoard.tileSize * 2)

		pygame.draw.rect(self.surface, GameBoard.menu_bg, pygame.Rect(x+5, y+5, w, h))
		pygame.draw.rect(self.surface, GameBoard.menu_fg, pygame.Rect(x, y, w, h))


	#Renders the lettering and numbering for each grid row and column.
	#TODO: works, but is messy. wouldn't hurt to fix.
	def _renderBoardText(self):
		#Create a font object to write with
		font = pygame.font.SysFont("monospace", 15)
		x = GameBoard.xOffset + (GameBoard.tileSize / 2)
		y = GameBoard.yOffset_top - GameBoard.tileSize

		for i in range(len(GameBoard.letters)):
			rLetter = font.render(GameBoard.letters[i], 1, pygame.Color("white"))
			self.surface.blit(rLetter, [x + (GameBoard.tileSize * i), y])

		x -= GameBoard.tileSize * 1.2
		y += (GameBoard.tileSize * 1.25)
		for i in range(len(GameBoard.letters)):
			rLetter = font.render(str(i+1), 1, pygame.Color("white"))
			self.surface.blit(rLetter, [x, y + (GameBoard.tileSize * i)])

		y = GameBoard.yOffset_bottom - GameBoard.tileSize + (GameBoard.tileSize * 1.25)
		for i in range(len(GameBoard.letters)):
			rLetter = font.render(str(i+1), 1, pygame.Color("white"))
			self.surface.blit(rLetter, [x, y + (GameBoard.tileSize * i)])

	def _renderGameName(self):
		font = pygame.font.SysFont("impact", 40)
		self.surface.blit(font.render("Naval", 1, pygame.Color("black")), [413, 38])
		self.surface.blit(font.render("Naval", 1, pygame.Color("lightgrey")), [410, 35])

		self.surface.blit(font.render("Commander", 1, pygame.Color("black")), [413, 78])
		self.surface.blit(font.render("Commander", 1, pygame.Color("lightgrey")), [410, 75])

	#Will render/re-render both grids, but not the textures.
	def _renderGrids(self):
		self.renderSingleGrid(GameBoard.TOP)
		self.renderSingleGrid(GameBoard.BOTTOM)

	#Renders a single grid as needed.
	def renderSingleGrid(self, gridSide):

		lineList = self.lineList_top if (gridSide == GameBoard.TOP) else self.linelist_bottom

		for i in range(0, len(lineList), 4):
			pygame.draw.line(self.surface, GameBoard.gridColor, lineList[i], lineList[i+1])
			pygame.draw.line(self.surface, GameBoard.gridColor, lineList[i+2], lineList[i+3])


	#Renders textures for both sides of the board.
	def _renderTextures(self):
		self.renderSingleTexture(GameBoard.TOP)
		self.renderSingleTexture(GameBoard.BOTTOM)

	#Renders the whole texture for the indicated side of the board
	def renderSingleTexture(self, gridSide):

		xOffset = GameBoard.xOffset
		yOffset = GameBoard.yOffset_top if (gridSide == GameBoard.TOP) else GameBoard.yOffset_bottom

		self.surface.blit(self.waterTexture, [xOffset, yOffset])


	#Returns rectangles contains the dimensions of the bottom and top grids.
	def bottomGridRectangle(self):
		return pygame.Rect(GameBoard.xOffset, GameBoard.yOffset_bottom, GameBoard.tileSize*(GameBoard.boardSize-1), GameBoard.tileSize*(GameBoard.boardSize-1))

	def topGridRectangle(self):
		return pygame.Rect(GameBoard.xOffset, GameBoard.yOffset_top, GameBoard.tileSize*(GameBoard.boardSize-1), GameBoard.tileSize*(GameBoard.boardSize-1))


	#Highlights tiles based upon the data entered by setTileToUpdate() method.
	def highlightTiles(self):
		#holds the side of to render the tiles.
		bSide = self._sideToUpdate

		xOffset = GameBoard.xOffset
		yOffset = GameBoard.yOffset_bottom if (bSide == GameBoard.BOTTOM) else GameBoard.yOffset_top

		for tile in self._tilesToUpdate:
			#r contains the destination rect to draw to
			r = pygame.Rect((tile[0]*GameBoard.tileSize)+xOffset+1, (tile[1]*GameBoard.tileSize)+yOffset+1, GameBoard.tileSize-1, GameBoard.tileSize-1)
			#s is the surface that will be drawn to r, it contains the color to make the tile
			#SRCALPHA is used to indicate we want to use the alpha value of the source color.
			s = pygame.Surface([GameBoard.tileSize-1, GameBoard.tileSize-1], SRCALPHA)

			#Set color and adjust the alpha value of the color to make it transparent
			color = pygame.Color(self._tileHighlightColor)
			color.a = 80
			s.fill(color)

			#Render the highlight!
			self.surface.blit(s, r)