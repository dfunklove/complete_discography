import sys
import re
import requests_with_caching
from bs4 import BeautifulSoup

"""
complete_discography.py

Assemble a complete HTML discography for an artist based on "Aliases" and "In Groups" data from Discogs.com.

Input: Artist name

Output: HTML page containing a table of all albums by all artists for which the given artist is an alias or a group member.

Written by Daniel Lovette
https://github.com/dfunklove
"""

PARSER = 'lxml'
BASE_URL = 'https://discogs.com/'

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

def find_alias_links(soup):
	return find_profile_links(soup, "Aliases")

def find_group_links(soup):
	return find_profile_links(soup, "In Groups")

def find_album_rows(context, soup):
	results = []
	table = soup.find(id="artist")
	if not table:
		return
	grab_next = False
	for row in table.find_all('tr'):
		if "Albums" in row.text:
			grab_next = True
		elif grab_next:
			if 'card' in row.get('class'):
				row['class'].remove('card')
				for img in row.find_all('img'):
					img['src'] = img.get('data-src')
				for button in row.find_all('button'):
					button.decompose()
				for catno in row.find_all(class_='catno_first'):
					catno.decompose()
				for sell in row.find_all(class_='sell_this_version'):
					sell.decompose()
				row = row.prettify()
				row = row.replace("href=\"/", "href=\""+BASE_URL)
				row = row.replace("href='/", "href='"+BASE_URL)
				results.append(row)
			else:
				break
	if context and len(results) > 0:
		context.publish_release_rows(results)
	return results

def find_url_for_artist(name):
	url = "https://www.discogs.com/search/"
	params = { 'type': 'artist', 'q': name }
	search_result = requests_with_caching.get(url, params)
	soup = BeautifulSoup(search_result.text, PARSER)
	return soup.find(id="search_results").a.get("href")

def get_discography(context, name):
	artist_url = find_url_for_artist(name)
	artist_page = requests_with_caching.get(BASE_URL + artist_url)
	soup = BeautifulSoup(artist_page.text, PARSER)
	alias_links = find_alias_links(soup)
	group_links = find_group_links(soup)

	# Find releases for groups
	album_rows = []
	for link in group_links.values():
		artist_page = requests_with_caching.get(BASE_URL + link)
		soup = BeautifulSoup(artist_page.text, PARSER)
		album_rows += find_album_rows(context, soup)

	# Find releases each alias and any groups for that alias
	for link in alias_links.values():
		artist_page = requests_with_caching.get(BASE_URL + link)
		soup = BeautifulSoup(artist_page.text, PARSER)
		album_rows += find_album_rows(context, soup)
		group_links = find_group_links(soup)
		for link in group_links.values():
			artist_page = requests_with_caching.get(BASE_URL + link)
			soup = BeautifulSoup(artist_page.text, PARSER)
			album_rows += find_album_rows(context, soup)

	if len(album_rows) == 0:
		context.publish_empty_result()

	retval = "<table>"
	for k in album_rows:
		retval += k
	retval += "</table>"
	return retval

#
# Main Program
#
if __name__ == "__main__":
	if (len(sys.argv) < 2):
		print("usage: python "+sys.argv[0]+" [artist name] > outfile.html")
		exit()

	print(get_discography(None, sys.argv[1]))
