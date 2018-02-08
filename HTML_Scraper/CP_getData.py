self.from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re

class Pokemon:
	def __init__(self):
		self.name = ""
		self.form = ""
		self.cat = ""
		self.type = []
		self.dexNum = -1
		self.height = -1
		self.weight = -1
		# EV/EXP info
		self.maxExp = 0
		self.expRate = ""
		self.evYield = []
		self.expYield = -1
		# Breed/friendship info
		self.eggGroup = ""
		self.hatchTime = ""
		self.baseFriend = -1
		self.catchRate = -1
	
	def printMon(self):
		print("Name: %s" % self.name)
		print("The %s Pokemon" % self.cat)
		print("National Dex Number: %d" % self.dexNum)
		if (len(self.form) != 0):
			print("Form: %s" % self.form)
		print("Type: ", end="")
		for count, type in enumerate(self.type):
			print(type, end="")
			if (count < (len(self.type) - 1)):
				print(" / ", end="")
		print("")
		
# Gather attributes for new Pokemon entity from its Bulbapedia page.
def parseBasicInfo(soup):
	newMon = {}
	allInfo = soup.find("div", {"id":"mw-content-text", "class":"mw-content-ltr"}) # Find block containing basic info
	allInfo = allInfo.find("table", {"class":"roundy"})  # Find table of basic info
	firstTr = allInfo.find('tr')
	allTr = [firstTr] + firstTr.find_next_siblings('tr') # Get list of each row in table
	# 1. Get name, category, and national dex number.
	getNameCatDex(allTr[0], newMon)
	fixForm(newMon)
	# 2. Get all typings for each form.
	getTypes(allTr[1], newMon)
	# 3. Get height/weight.
	# Check new pokemon.
	for p in newMon:
		newMon[p].printMon()

# Get all names and category from some Pokemon page. If multiple names
# then multiple forms so create a new object for each form.
# Category and dex are consistent across all forms.
def getNameCatDex(parentRow, newMon):
	nameAndNumRow = parentRow.find("tr")
	name = parentRow.find("big").getText()
	imageParent = nameAndNumRow.find_next_sibling("tr")
	firstImageRow = imageParent.find("tr")
	imageRows = [firstImageRow] + firstImageRow.find_next_siblings("tr")
	for r in imageRows[:-1]:
		if (r.has_attr("style")):
			if (r["style"].find("none") != -1):
				continue
		allTD = r.find_all("td")
		for d in allTD:
			if (d.has_attr("style")):
				if (d["style"].find("none") != -1):
					continue
			formLink = d.find("a")
			if (formLink != None):
				if (formLink.has_attr("title")):
					form = formLink["title"]
				else:
					form = None
			else:
				form = None
			# If new name found, create new Pokemon object.
			if (form != None):
				newPoke = Pokemon()
				newPoke.name = name
				newPoke.form = form
				newMon[form] = newPoke	
	# If Pokemon does not have multiple forms, get name from diff block.
	if (len(newMon) == 0):
		newPoke = Pokemon()
		newPoke.name = name
		newMon[name] = newPoke
	catTag = parentRow.find("a", {"href":"/wiki/Pok%C3%A9mon_category"})
	cat = catTag.getText()[:-8]
	dexBlock = parentRow.find("th", {"class":"roundy"}).getText()
	findDexNum = '#([0-9]+)'
	result = re.search(findDexNum, dexBlock)
	dexNum = result.group(1)
	for each in newMon:
		newMon[each].cat = cat
		newMon[each].dexNum = int(dexNum)
	return 0

def fixForm(newMon):
	for m in newMon:
		name = newMon[m].name
		form = newMon[m].form
		newMon[m].form = form.replace(name, "")
		
def getTypes(parentRow, newMon):
	firstTypeRow = parentRow.find("tr")
	typeRows = [firstTypeRow] + firstTypeRow.find_next_siblings("tr")
	for r in typeRows:
		firstType = r.find("td")
		eachType = [firstType] + firstType.find_next_siblings("td")
		for d in eachType:
			if (d.has_attr("style")):
				if (d["style"].find("none") != -1):
					continue
			name = d.find("small")
			if (name != None):
				name = name.getText()
			typeList = []
			typePair = d.find("td")
			typePair = [typePair] + typePair.find_next_siblings("td")
			for t in typePair:
				newType = ""
				if (t.has_attr("style")):
					if (t["style"].find("none") != -1):
						continue
				typeLink = t.find("a")
				if (typeLink.has_attr("title")):
					newType = typeLink["title"][:-7]
				if (len(newType) != 0):
					typeList.append(newType)
			if (len(typeList) != 0):
				if (name != None):
					for t in typeList:
						newMon[name].type.append(t)
				else:
					for key in newMon:
						for t in typeList:
							newMon[key].type.append(t)
	return 0
	
# Return HTML document returned by URL access. Attempts URL access upto
# 15 times, returning -1 if unsuccessful.
def openURL(url):
	maxAttempts = 15
	while (maxAttempts > 0):
		try:
			req = Request(url, headers={'User-Agent': 'Mozilla'})
			resp = urlopen(req)
			return resp
		except:
			maxAttempts -= 1
	return -1

if (__name__ == "__main__"):
	url = "https://bulbapedia.bulbagarden.net/wiki/Rotom_(Pok%C3%A9mon)"
	resp = openURL(url)
	soup = BeautifulSoup(resp, "lxml")

	parseBasicInfo(soup)