class GameState:

	#menus
	MainMenu = 0
	Paused = 1

	#playing states
	#MinPlayingState is the lowest state that indicates we are playing the game.
	MinPlayingState = 10
	ShipPlacement = 10
	Attacking = 11
	Defending = 12
	ShipWasSunk = 13
	GameOver = 14