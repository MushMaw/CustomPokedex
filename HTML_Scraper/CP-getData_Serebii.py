'''
Custom Pokedex - Verson 0.1
Module: getData (Serebii)
'''


from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from CP-PokemonClass import Pokemon
import re


def getAllPokemon(url):
	resp = openURL(url)
	if (resp == -1):
		return resp
	PokemonDict = {}
	
	gatherTableInfo(resp, PokemonDict)
		
def gatherTableInfo(resp, PokemonDict):
	soup = BeautifulSoup(resp, "lxml")
	
	dexTableTag = soup.find("table", {"class":"dextable"})
	parseDexTable(dexTableTag, PokemonDict)
	

def parseDexTable(dexTableTag, PokemonDict):
	

	
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
	return 0