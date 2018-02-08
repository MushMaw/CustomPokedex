'''

'''

class Pokemon:
	STAT_NAMES = ["hp", "attack", "defense", "sp. attack", "sp. defense", "speed"]
	BASE_FILE_NAME = "pokemonObject_"
	HEIGHT_IMPERIAL_FORMAT = '''([0-9]+'[0-9]*")'''
	DECIMAL_FORMAT = "([0-9]+.*[0-9]*)"
	HEIGHT_METRIC = "m"
	WEIGHT_MEASURES = ["lbs", "kg"]
	CATCH_RATE_FORMAT = "([0-9]+)(\([a-zA-Z0-9_]+\))"
	
	def __init__(self):
		# Dextable info
		self.name = "" #
		self.category = "" #
		self.forms = [] #
		self.types = {} #
		self.genderChances = {} #
		self.dexNumber = 0 #
		self.height = {} #
		self.weight = {} #
		self.eggSteps = {} #
		self.captureRate = {} #
		self.expRate = ""#
		self.maxExp = -1#
		self.evYield = {} #
		self.baseHappiness = -1 #
		self.stats = {}
		self.statTotal = 0
		
	def dexToString(self):
		output = str(self.dexNumber)
		while (len(output) < 3):
			output = "0" + output
		return output
		
	def printThis(self):
		print(self.name + "  |  " + self.category + "  |  #" + self.dexToString())
		for each in self.types:
			print(each + " : ", self.types[each])
		for each in self.genderChances:
			print(each + " : " + self.genderChances[each])
		for each in self.captureRate:
			print(each + " : " + self.captureRate[each])
		print("Base Egg Steps: " + self.eggSteps)
		print("Max EXP: " + str(self.maxExp) + " at a rate of " + self.expRate)
		print("Base Happiness: ", self.baseHappiness)
		print(self.evYield)
		print(self.stats)
		print(self.statTotal)
		print(self.forms)
		
class MegaPokemon(Pokemon):

	def __init__(self):
		super().__init__()