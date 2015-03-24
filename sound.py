# *** Imports ***
import pygame, sys, os
from pygame.locals import *



class Sound:

	#Sound icon location.
	icon = "image\\Sound.png"

	def __init__(self, surface):
		self.surface = surface
		self.isMute = False

		#x/y to draw to
		self.x, self.y = 600, 700

		#Scale the image
		size = 40
		self.icon = pygame.transform.scale(pygame.image.load(Sound.icon), [size, size])

		self.iconLocation = pygame.Rect(self.x, self.y, size, size)

		#First rectangle draws whole icon, second rectangle remove the sound waves coming from the speaker to show if we are mute or not.
		self.drawRect = { False: pygame.Rect(0, 0, self.icon.get_width(), self.icon.get_height()),
						  True: pygame.Rect(0, 0, 25, self.icon.get_height())}

		#Dictionary of sound to play.
		self.soundDict = {} 
		self.soundDict.update({"missed_hit": pygame.mixer.Sound("sound\\hit_miss.wav")})
		self.soundDict.update({"hit": pygame.mixer.Sound("sound\\hit.wav")})

	#plays a sound based on the sound variable.
	def play(self, sound):
		if (not self.isMute):
			if (self.soundDict.has_key(sound)):
				self.soundDict[sound].play()
			else:
				print "Sound \"" + sound + "\" not found."

	#Check if sound icon was clicked, mute/unmute sound.
	def update(self, main):
		if (main.inp.mouseClicked[0] == 1 and main.inp.prevMouseClicked[0] != 1):
			if (self.iconLocation.collidepoint(pygame.mouse.get_pos())):
				#Change isMute bool
				self.isMute = (not self.isMute)
				#Update background to the redraw reflects properly.
				main.gameBoard.updateBackground = True

	#Draw sound icon
	def render(self):
		self.surface.blit(self.icon, [self.x, self.y], area=self.drawRect[self.isMute])