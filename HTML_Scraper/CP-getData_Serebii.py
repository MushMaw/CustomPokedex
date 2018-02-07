'''
Custom Pokedex - Verson 0.1
Module: getData (Serebii)
'''


from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from CP_PokemonClass import Pokemon
import re


def getInfoForPokemon(url, newMon):
	resp = openURL(url)
	if (resp == -1):
		return resp
	print("Connected")
	gatherTableInfo(resp, newMon)
		
def gatherTableInfo(resp, PokemonDict):
	soup = BeautifulSoup(resp, "lxml")
	
	firstDexTableTag = soup.find("table", {"class":"dextable"})
	parseDexTable(firstDexTableTag, PokemonDict)
	
def parseDexTable(dexTableTag, newMon):
	tableRow = dexTableTag.find("tr").find_next_sibling()
	checkRow = tableRow.find("td").find_next_sibling()
	newMon.name = checkRow.getText()
	
	checkRow = tableRow.find("td", {"class":"cen"})
	getTypesForForms(checkRow, newMon.name, newMon.types)
	for form in newMon.types:
		newMon.forms.append(form)
		
	checkRow = checkRow.find_previous_sibling()
	getGenderChances(checkRow, newMon.genderChances)
	
	tableRow = findSibling_n(tableRow, 2, None)
	td_Tag = tableRow.find("td")
	newMon.category = td_Tag.getText()
	td_Tag = td_Tag.find_next_sibling()
	getStature(td_Tag, newMon.forms, newMon.height, "h")
	td_Tag = td_Tag.find_next_sibling()
	getStature(td_Tag, newMon.forms, newMon.weight, "w")
	
def getStature(checkTag, formList, outputDict, mode):
	baseString = checkTag.getText()
	print(baseString)
	n = len(formList)
	formatList = []
	if (mode == "h"):
		formatList = Pokemon.HEIGHT_FORMATS
	else:
		for measure in Pokemon.WEIGHT_MEASURES:
			formatList.append(Pokemon.WEIGHT_FORMAT + measure)
	for count, format in enumerate(formatList):
		regExp = HW_buildRegExp(format, n)
		m = re.search(regExp, baseString)
		for i in range(n):
			key = formList[i]
			value = m.group(i+1)
			if (mode == "w"):
				value += Pokemon.WEIGHT_MEASURES[count]
			if (key not in outputDict):
				outputDict[key] = [value]
			else:
				outputDict[key].append(value)

def HW_buildRegExp(regUnit, n):
	spacing = " / "
	regExp = regUnit
	for i in range(n-1):
		regExp += (spacing + regUnit)
	return regExp

def getTypesForForms(checkRow, mainName, typeDict):
	allTypeRows = [checkRow.find("tr")]
	if (allTypeRows[0] != None):
		allTypeRows += allTypeRows[0].find_next_siblings()
		for tRow in allTypeRows:
			tdTag = tRow.find("td")
			formName = tdTag.getText()
			allTypes = getEachTypeForRow(tdTag.find_next_sibling())
			typeDict[formName] = allTypes
	else:
		allTypes = getEachTypeForRow(checkRow)
		typeDict[mainName] = allTypes
	return typeDict

def getGenderChances(checkRow, genderDict):
	genderRow = checkRow.find("tr")
	if (genderRow != None):
		eachGender = [genderRow] + genderRow.find_next_siblings()
		for g in eachGender:
			g_td = g.find("td")
			genderName = g_td.find(text=True, recursive=False)
			genderChance = g_td.find_next_sibling().getText()
			genderDict[genderName] = genderChance
	return genderDict
	
def findSibling_n(soup, n, tag):
	end = soup
	while (n > 0):
		if (tag != None):
			next = end.find_next_sibling(tag)
		else:
			next = end.find_next_sibling()
		if (next == None):
			break
		else:
			end = next
		n -= 1
	if (end == soup):
		return None
	return end
	
def getEachTypeForRow(checkRow):
	allTypes = []
	allTypeTags = checkRow.findAll("a")
	typeRegExp = "/(\w+).gif"
	for typeTag in allTypeTags:
		typeText = typeTag.find("img")["src"]
		type = re.search(typeRegExp, typeText).group(1)
		allTypes.append(type)
	return allTypes

def openURL(url):
	maxAttempts = 15
	while (maxAttempts > 0):
		try:
			req = Request(url, headers={'User-Agent':'Mozilla'})
			resp = urlopen(req)
			return resp
		except:
			maxAttempts -= 1
	return -1

if (__name__ == "__main__"):
	for i in range(5):
		dexNum = 2
		newMon = Pokemon()
		newMon.dexNumber = dexNum
		url = "https://www.serebii.net/pokedex-sm/" + newMon.dexToString() + ".shtml"
		getInfoForPokemon(url, newMon)
		newMon.printThis()