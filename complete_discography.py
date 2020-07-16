import sys
import re
import requests_with_caching
from bs4 import BeautifulSoup

"""
complete_discography.py

Assemble a complete HTML discography for an artist based on "Aliases" and "In Groups" data from Discogs.com.

Input: Artist name

Output: HTML page containing a table of all albums by all artists for which the given artist is an alias or a group member.

Usage: python complete_discography.py [artist name] > outfile.html

Written by Daniel Lovette
https://github.com/dfunklove
"""

PARSER = 'lxml'
BASE_URL = 'https://discogs.com'

def find_profile_links(soup, search_string):
	""" Find links in html based on the class and string content of a div """

	profile_links = {}
	div_prefix = soup.find('div', class_='head', string=re.compile(search_string))
	if div_prefix:
		for s in div_prefix.next_siblings:
			if s.name == 'div':  # Found the aliases!
				for a in s.find_all('a'):
					profile_links[a.text] = a.get('href')
				break
	return profile_links

def find_related_artist_links(soup):
	return {**find_profile_links(soup, "Aliases"), **find_profile_links(soup, "In Groups")}

def find_album_rows(soup):
	results = []
	table = soup.find(id="artist")
	grab_next = False
	for row in table.find_all('tr'):
		if "Albums" in row.text:
			grab_next = True
		elif grab_next:
			if 'card' in row.get('class'):
				results.append(row.prettify())
			else:
				break
	return results

def find_url_for_artist(name):
	url = "https://www.discogs.com/search/"
	params = { 'type': 'artist', 'q': name }
	search_result = requests_with_caching.get(url, params)
	soup = BeautifulSoup(search_result.text, PARSER)
	return soup.find(id="search_results").a.get("href")

def complete_discography(name):
	artist_url = find_url_for_artist(name)
	artist_page = requests_with_caching.get(BASE_URL + artist_url)
	soup = BeautifulSoup(artist_page.text, PARSER)
	artist_links = find_related_artist_links(soup)

	album_rows = []
	for a in artist_links.keys():
		artist_page = requests_with_caching.get(BASE_URL + artist_links[a])
		soup = BeautifulSoup(artist_page.text, PARSER)
		album_rows += find_album_rows(soup)

	print("<html><body><table>")
	for k in album_rows:
		k = k.replace("href=\"", "href=\""+BASE_URL);
		k = k.replace("href='", "href='"+BASE_URL);
		print(k)
	print("</table></body></html>")

#
# Main Program
#
if (len(sys.argv) < 2):
	print("Usage: python "+sys.argv[0]+" [artist name] > outfile.html")
	exit()

complete_discography(sys.argv[1])