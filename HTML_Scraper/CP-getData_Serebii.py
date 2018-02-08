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
		
def gatherTableInfo(resp, newMon):
	soup = BeautifulSoup(resp, "lxml")
	
	dexTableTag = soup.find("table", {"class":"dextable"})
	parseFirstDexTable(dexTableTag, newMon)
	dexTableTag = dexTableTag.find_next_sibling("table", {"class":"dextable"})
	parseSecondDexTable(dexTableTag, newMon)
	
def parseFirstDexTable(dexTableTag, newMon):
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
	
	td_Tag = td_Tag.find_next_sibling()
	catchRateString = td_Tag.getText().replace(" ", "")
	getCatchRate(catchRateString, newMon)
	
	td_Tag = td_Tag.find_next_sibling()
	newMon.eggSteps = td_Tag.getText()

def parseSecondDexTable(dexTableTag, newMon):
	tableRow = dexTableTag.find("tr")
	tableRow = findSibling_n(tableRow, 3, None)
	td_Tag = tableRow.find("td")
	getExpMaxAndRate(td_Tag.getText(), newMon)
	
	td_Tag = td_Tag.find_next_sibling()
	newMon.baseHappiness = td_Tag.getText()
	
	td_Tag = td_Tag.find_next_sibling()
	getEffortValues(baseString, newMon)

def getExpMaxAndRate(expString, newMon):
	maxExp_reg = "([0-9]*,*[0-9]*,*[0-9]*) Points"
	m = re.search(maxExp_reg, expString)
	maxExp = m.group(1)
	newMon.maxExp = int(maxExp.replace(",", ""))
	
	expString = expString.replace(m.group(0), "")
	newMon.expRate = expString

def getEffortValues(baseString, newMon):
	

def getStature(checkTag, formList, outputDict, mode):
	baseString = checkTag.getText()
	n = len(formList)
	formatList = []
	if (mode == "h"):
		formatList = [Pokemon.HEIGHT_IMPERIAL_FORMAT, Pokemon.DECIMAL_FORMAT + Pokemon.HEIGHT_METRIC]
	else:
		for measure in Pokemon.WEIGHT_MEASURES:
			formatList.append(Pokemon.DECIMAL_FORMAT + measure)
	for count, format in enumerate(formatList):
		regExp = HW_buildRegExp(format, n)
		m = re.search(regExp, baseString)
		if (m == None):
			regExp = format
			m = re.search(regExp, baseString)
		for i in range(n):
			key = formList[i]
			if (regExp == format):
				groupIndex = 1
			else:
				groupIndex = i+1
			value = m.group(groupIndex)
			if (mode == "w"):
				value += Pokemon.WEIGHT_MEASURES[count]
			if (key not in outputDict):
				outputDict[key] = [value]
			else:
				outputDict[key].append(value)

def getCatchRate(baseString, newMon):
	m = re.search(Pokemon.CATCH_RATE_FORMAT, baseString)
	while (m != None):
		key = m.group(2)
		value = m.group(1)
		newMon.captureRate[key] = value
		baseString = baseString.replace(m.group(0), "")
		m = re.search(Pokemon.CATCH_RATE_FORMAT, baseString)
		print("That's one")
	if (len(newMon.captureRate) == 0):
		numExp = "([0-9]+)"
		m = re.search(numExp, baseString)
		if (m != None):
			newMon.captureRate["all"] = m.group(1)

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
	for i in range(1):
		dexNum = i+800
		newMon = Pokemon()
		newMon.dexNumber = dexNum
		url = "https://www.serebii.net/pokedex-sm/" + newMon.dexToString() + ".shtml"
		getInfoForPokemon(url, newMon)
		newMon.printThis()