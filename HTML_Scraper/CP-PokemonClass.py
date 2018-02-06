'''

'''


class Pokemon:
	STAT_NAMES = ["hp", "attack", "defense", "sp. attack", "sp. defense", "speed"]
	BASE_FILE_NAME = "pokemonObject_"
	
	def __init__(self):
		# Dextable info
		self.name = ""
		self.category = ""
		self.form = ""
		self.type = []
		self.dexNumber = 0
		self.height = -1
		self.weight = -1
		self.eggSteps = -1
		self.captureRate = -1
		
		self.expRate = ""
		self.maxExp = -1
		self.expYield = -1
		self.evYield = {}
		for stat in Pokemon.STAT_NAMES:
			self.evYield[stat] = 0
			
		self.eggGroup = ""
		self.baseHappiness = -1
		