import json
import logging
import re
import traceback
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
	target = soup.find(string=search_string)
	if target:
		for a in target.parent.parent.parent.find('td').find_all('a'):
			profile_links[a.text] = a.get('href')
	return profile_links

def find_alias_links(soup):
	return find_profile_links(soup, "Aliases")

def find_group_links(soup):
	return find_profile_links(soup, "In Groups")

def find_album_rows(url, context=None):
	# Results are paginated so we must keep fetching until they are blank.
	# Assume results will be empty if we go beyond the last page.
	album_rows = []
	temp_rows = []
	page = 1
	while page == 1 or (len(temp_rows) > 0 and page <= 50):
		artist_page = requests_with_caching.get(url, {'page':page})
		soup = BeautifulSoup(artist_page.text, PARSER)
		temp_rows = find_album_rows_in_page(soup, context)
		album_rows += temp_rows
		page += 1
	return album_rows

def find_album_rows_in_page(soup, context=None):
	"""
	In the given soup, find the table rows which contain album information.
	Pass the results to the context before returning them.

	Required Parameters:
	soup: a BeautifulSoup object

	Optional Parameters:
	context: an object which has the methods publish_release_rows and publish_complete
	"""
	albums = []
	results = []
	dsdata = soup.find(id="dsdata")
	if not dsdata:
		return results
	data = json.loads(dsdata.string)["data"]
	for key in data.keys():
		if key.startswith("Release"):
			release = data[key]
			album = {}
			album["released"] = release["released"]
			album["siteUrl"] = release["siteUrl"]
			album["title"] = release["title"]
			if release["labelsNew"] != None and len(release["labelsNew"]) > 0:
				album["label"] = release["labelsNew"][0]["displayName"]
			else:
				album["label"] = ""
			artists = []
			for artist in release["primaryArtists"]:
				artists.append(artist["displayName"])
			album["artists"] = artists
			imageRef = None
			try:
				imageRef = release['images({\"first\":1})']["edges"][0]["node"]["__ref"]
				album["artUrl"] = data[imageRef]["tiny"]["__ref"][24:]
			except:
				album["artUrl"] = ""
			albums.append(album)
	for album in albums:
		row = '<tr>'
		row += f"<td><a href=\"{album['siteUrl']}\"><img src=\"{album['artUrl']}\"></a></td>"
		row += '<td>'
		if len(album['artists']) > 1:
			row += " / ".join(album['artists']) + " - "
		row += f"<a href=\"{album['siteUrl']}\">{album['title']}</a></td>"
		row += f"<td>{album['label']}</td>"
		row += f"<td>{album['released']}</td>"
		row += '</tr>'
		results.append(row)
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
		album_rows = find_album_rows(BASE_URL + artist_url, context)

		# Find releases for groups
		for link in group_links.values():
			album_rows += find_album_rows(BASE_URL + link, context)

		# Find releases each alias
		for link in alias_links.values():
			album_rows += find_album_rows(BASE_URL + link, context)

		if context:
			context.publish_complete()

		logging.getLogger(__name__).info("Fetch complete")

		retval = "<table>"
		for k in album_rows:
			retval += k
		retval += "</table>"
		return retval

	except BaseException as e:
		if context:
			context.publish_error("Invalid response from music database")
		logging.getLogger(__name__).error(traceback.format_exc())
		return None