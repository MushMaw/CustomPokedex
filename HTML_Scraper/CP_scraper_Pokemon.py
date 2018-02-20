'''
Custom Pokedex - Verson 0.1
Module: getData (Serebii)
'''


from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from CP_Pokemon_class import Pokemon, MegaPokemon
import re
import sys


def getInfoForPokemon(url, newMon):
	resp = openURL(url)
	if (resp == -1):
		return resp
	print("Connected")
	gatherTableInfo(resp, newMon)
		
def gatherTableInfo(resp, newMon):
	soup = BeautifulSoup(resp, "lxml")
	
	pictureTableTag = soup.find("table", {"class":"dextable"})
	parsePictureTable(pictureTableTag, newMon, False)
	
	happinessTableTag = pictureTableTag.find_next_sibling("table", {"class":"dextable"})
	parseHappinessTable(happinessTableTag, newMon)
	
	formTable = soup.find("td", text="Alternate Forms")
	if (formTable != None):
		formTable = formTable.parent.find_next_sibling()
		formTable = formTable.find("tr")
		findMissedForms(formTable, newMon)
	
	statsTag = soup.find("a", {"name":"stats"}).find_next_sibling()
	newMon.stats[newMon.name] = parseStatsTable(statsTag)
	
	# Check for megas.
	megaSoup = soup.find("a", {"name":"mega"})
	if (megaSoup != None):
		megaSoup = megaSoup.find_next_sibling()
		while (megaSoup != None):
			newMega = MegaPokemon()
			parsePictureTable(megaSoup, newMega, True)
			megaSoup = megaSoup.find_next_sibling("a", {"name":"megastats"})
			megaSoup = megaSoup.find_next_sibling()
			newMega.stats[newMega.name] = parseStatsTable(megaSoup)
			newMon.megaEvos[newMega.name] = newMega
			megaSoup = megaSoup.find_next_sibling("table", {"class":"dextable"})
			
	findFormStats(soup, newMon)

def findFormStats(soup, newMon):
	baseSearchString = "Stats - "
	altFormString = "Alternate Forms"
	terms = newMon.forms[:] + [altFormString]
	for count, t in enumerate(terms):
		searchString = baseSearchString + t
		statsTable = soup.find("b", text=re.compile(searchString))
		if (statsTable != None):
			# Navigate over to statsTable
			statsTable = statsTable.parent.parent.parent
			newStats = parseStatsTable(statsTable)
			if (count == len(terms) - 1):
				# Alternate Forms table found, so apply distribution
				# to all alternate forms.
				for form in newMon.forms:
					if (form != newMon.name):
						newMon.stats[form] = newStats
			else:
				newMon.stats[t] = newStats
	for form in newMon.forms:
		if (form not in newMon.stats):
			newMon.stats[form] = newMon.stats[newMon.name]

def parsePictureTable(dexTableTag, newMon, isMega):
	tableRow = dexTableTag.find("tr").find_next_sibling()
	if (isMega):
		tableRow = tableRow.find_next_sibling()
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

def parseHappinessTable(dexTableTag, newMon):
	tableRow = dexTableTag.find("tr")
	tableRow = findSibling_n(tableRow, 3, None)
	td_Tag = tableRow.find("td")
	getExpMaxAndRate(td_Tag.getText(), newMon)
	
	td_Tag = td_Tag.find_next_sibling()
	newMon.baseHappiness = td_Tag.getText()
	
	td_Tag = td_Tag.find_next_sibling()
	getEffortValues(td_Tag.getText(), newMon)

def findMissedForms(dexTableTag, newMon):
	allForms = dexTableTag.find_all("td")
	for formTag in allForms:
		form = formTag.getText()
		if form not in newMon.forms:
			newMon.forms.append(form)
	
def parseStatsTable(dexTableTag):
	row = dexTableTag.find("tr").find_next_sibling()
	statNameOrder = []
	column = row.find("td").find_next_sibling()
	statOrder = []
	while (column != None):
		statOrder.append(column.getText().lower())
		column = column.find_next_sibling()
	row = row.find_next_sibling()
	column = row.find("td").find_next_sibling()
	i = 0
	newStats = {}
	while (column != None):
		statValue = int(column.getText())
		newStats[statOrder[i]] = statValue
		i += 1
		column = column.find_next_sibling()
	return newStats
	

def getExpMaxAndRate(expString, newMon):
	maxExp_reg = "([0-9]*,*[0-9]*,*[0-9]*) Points"
	m = re.search(maxExp_reg, expString)
	maxExp = m.group(1)
	newMon.maxExp = int(maxExp.replace(",", ""))
	
	expString = expString.replace(m.group(0), "")
	newMon.expRate = expString

def getEffortValues(baseString, newMon):
	subStrings = getSubstrings(baseString.lower(), newMon.forms)
	evRegExp = "([0-9]+) %s point\(s\)"
	for count, subStr in enumerate(subStrings):
		formEv = {}
		for stat in Pokemon.STAT_NAMES:
			statReg = evRegExp % stat
			m = re.search(statReg, subStr)
			if (m != None):
				value = int(m.group(1))
				formEv[stat] = value
			else:
				formEv[stat] = 0
		if (len(subStrings) == 1):
			newMon.evYield[newMon.name] = formEv
		else:
			newMon.evYield[newMon.forms[count]] = formEv
	
def getSubstrings(baseString, splitByList):
	formIndices = []
	for form in newMon.forms:
		index = baseString.find(form)
		if (index == -1):
			return [baseString]
		formIndices.append(index)
	formIndices.append(len(baseString) - 1)
	subStrings = []
	for i in range(len(newMon.forms)):
		j = formIndices[i]
		k = formIndices[i+1]
		subStrings.append(baseString[j:k])
	return subStrings

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
	for i in range(151):
		if (len(sys.argv) > 1):
			dexNum = i + int(sys.argv[1])
		else:
			dexNum = i
		newMon = Pokemon()
		newMon.dexNumber = dexNum
		url = "https://www.serebii.net/pokedex-sm/" + newMon.dexToString() + ".shtml"
		if (getInfoForPokemon(url, newMon) == -1):
			print(url)
			# Log the connection error.
			pass
		else:
			newMon.printThis()