import sys
import re
from complete_discography import requests_with_caching
from bs4 import BeautifulSoup

"""
complete_discography.py

Assemble a complete HTML discography for an artist based on "Aliases" and 
"In Groups" data from Discogs.com.

Input: Artist name

Output: HTML page containing a table of all albums by all artists for which the 
given artist is an alias or a group member.

Written by Daniel Lovette
https://github.com/dfunklove
"""

PARSER = 'lxml'
BASE_URL = 'https://discogs.com/'
DEFAULT_PARAMS = { 'limit': '500' }
EXCLUDED_COLUMNS = re.compile('catno|catno_first|country|sell_this_version|hide_mobile|hide-desktop|actions')

def find_profile_links(soup, search_string):
	"""
	Find links in html based on the class and string content of a div

	Required Parameters:
	soup: a BeautifulSoup object
	search_string: the type of link to search for; must match html exactly
	"""

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

def find_album_rows(soup, context=None):
	"""
	In the given soup, find the table rows which contain album information.
	Pass the results to the context before returning them.

	Required Parameters:
	soup: a BeautifulSoup object

	Optional Parameters:
	context: an object which has the methods publish_release_rows and publish_complete
	"""

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
				for a in row.find_all('a'):
					a['target'] = '_blank'
					a['rel'] = 'noreferrer noopener'
				for td in row.find_all(class_=EXCLUDED_COLUMNS):
					td.decompose()
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

def get_discography(name, context=None):
	"""
	Query discogs database to get all albums on which the given artist,  
	specified by "name", has appeared.

	Pass the results, as html table rows, to the context before returning them.

	Required Parameters:
	name: the name of the artist to search for

	Optional Parameters:
	context: an object which has the methods publish_release_rows and publish_complete
	"""

	try:
		artist_url = find_url_for_artist(name)
		artist_page = requests_with_caching.get(BASE_URL + artist_url, DEFAULT_PARAMS)
		soup = BeautifulSoup(artist_page.text, PARSER)
		alias_links = find_alias_links(soup)
		group_links = find_group_links(soup)
		album_rows = find_album_rows(soup, context)

		# Find releases for groups
		for link in group_links.values():
			artist_page = requests_with_caching.get(BASE_URL + link, DEFAULT_PARAMS)
			soup = BeautifulSoup(artist_page.text, PARSER)
			album_rows += find_album_rows(soup, context)

		# Find releases each alias and any groups for that alias
		for link in alias_links.values():
			artist_page = requests_with_caching.get(BASE_URL + link, DEFAULT_PARAMS)
			soup = BeautifulSoup(artist_page.text, PARSER)
			album_rows += find_album_rows(soup, context)
			group_links = find_group_links(soup)
			for link in group_links.values():
				artist_page = requests_with_caching.get(BASE_URL + link, DEFAULT_PARAMS)
				soup = BeautifulSoup(artist_page.text, PARSER)
				album_rows += find_album_rows(soup, context)

		if context:
			context.publish_complete()

		retval = "<table>"
		for k in album_rows:
			retval += k
		retval += "</table>"
		return retval

	except:
		if context:
			context.publish_error("Invalid response from music database")
		return None