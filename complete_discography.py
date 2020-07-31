import json
import sys
import re
from . import requests_with_caching

"""
complete_discography.py

Assemble a complete discography for an artist based on "Aliases" and "In Groups" data from Discogs.com.

Input: Artist name

Output: HTML table of all albums by all artists for which the given artist is an alias or a group member.

Usage: python complete_discography.py [artist name] > outfile.html

Written by Daniel Lovette
https://github.com/dfunklove
"""

PARSER = 'lxml'
BASE_URL = 'https://api.discogs.com'
API_KEY = 'EtNnhmPqmhSULCVJHRRx'
API_SECRET = 'VLSajjYuNLcuDKeRQzmrwwhnKlRYBLsn'
AUTH_PARAMS = { 'key': API_KEY, 'secret': API_SECRET }
DEFAULT_HEADERS = { 'user-agent': 'dfunklove_Complete_Discography/0.1 +https://dlove.it' }
DEBUG = True

def find_artists(name):
	"Query the discogs api to get an artist id for the given name"

	if not name:
		return None

	url = BASE_URL + "/database/search"
	params = AUTH_PARAMS.copy()
	name = name.strip()
	params['q'] = name
	params['type'] = 'artist'
	response = requests_with_caching.get(url, params=params, headers=DEFAULT_HEADERS)
	return json.loads(response.text)['results']


def artist_html(artist_info):
	thumb = artist_info['thumb']
	id = artist_info['id']
	name = artist_info['title']
	if not thumb:
		thumb = "images/artist_empty.svg"
	return f'<div class="artist"><a href="#" class="artist_thumb artist_link" artist_id="{id}" artist_name="{name}"><img src="{thumb}"/></a><a href="#" class="artist_name artist_link" artist_id="{id}" artist_name="{name}">{name}</a></div>'


def find_artist_info(artist_id):
	"Query the discogs api to get info for the given artist id"

	if not artist_id:
		return None

	url = f"{BASE_URL}/artists/{artist_id}"
	response = requests_with_caching.get(url, params=AUTH_PARAMS, headers=DEFAULT_HEADERS)
	return json.loads(response.text)


def find_releases(artist_id):
	"Query the discogs api to get all releases for the given artist id"

	if artist_id:
		params = AUTH_PARAMS.copy()
		params['per_page'] = 100
		return find_releases_on_page(f"{BASE_URL}/artists/{artist_id}/releases", params)
	else:
		return {}


def find_releases_on_page(url, params=None):
	"""
	Return a dict of all releases from the given page and all following pages,
	keyed on discogs id to avoid duplication
	"""

	response = requests_with_caching.get(url, params=params, headers=DEFAULT_HEADERS)
	result = json.loads(response.text)
	
	if DEBUG:
		print(response.url)
		print(json.dumps(result, indent=2))

	# put results in a dict to guarantee uniqueness
	retval = {}
	if 'releases' in result:
		for i in result['releases']:
			if i['role']=='Main':
				retval[i['id']] = i

	# if not found on this page, get the next one
	try:
		url = result['pagination']['urls']['next']
		retval.update(find_releases_on_page(url))
	except KeyError:
		pass

	return retval
	

def stats(artist_name, releases):
	retval = f'<table id="stats" class="stats"><tr><th class="text-cell">Total</th><th class="number-cell">{len(releases)}</th>'

	artist_counts = {}
	for r in releases:
		name = r['artist']
		if name in artist_counts:
			artist_counts[name] += 1
		else:
			artist_counts[name] = 1

	retval += f'<tr><td class="text-cell">{artist_name}</td><td class="number-cell">{artist_counts.pop(artist_name, 0)}</td></tr>'

	for a in sorted(artist_counts.keys()):
		retval += f'<tr><td class="text-cell">{a}</td><td class="number-cell">{artist_counts[a]}</td></tr>'
	retval += '</table>'
	return retval


def disco_table(releases):
	"Accept release data from discogs api and put it in an html table"

	# artist title label catno country year

	fields = ['artist', 'title', 'label', 'year']
	output = "<table><tr>"
	output += "<th></th>" # thumbnail column
	for f in fields:
		pretty = f.capitalize()
		output += f"<th>{pretty}</th>"
	output += "</tr>\n"
	for r in releases:
		output += "<tr>"
		if 'thumb' in r:
			output += f"<td><img src='{r['thumb']}'/></td>"
		else:
			output += f"<td></td>"

		for f in fields:
			if f in r:
				output += f"<td>{r[f]}</td>"
			else:
				output += "<td></td>"
		output += "</tr>\n"
	output += "</table>"

	return output


"""
PUBLIC FUNCTIONS
"""


def get_artists(name):
	"""
	Return a string of html representing a list of artists which match the given name
	"""
	artist_list = find_artists(name)
	result = ""
	for a in artist_list:
		result += artist_html(a)
	return result


def get_discography(artist_id):
	"""
	Assemble a complete html discography for an artist based on "Aliases" and "In Groups" data from Discogs.com

	Input: artist id from Discogs.com
	Output: html table of releases by artist
	"""

	empty_result = "No results found."
	
	if not artist_id:
		return empty_result

	all_releases = find_releases(artist_id)

	artist_info = find_artist_info(artist_id)
	if DEBUG:
		print(json.dumps(artist_info, indent=2))

	if 'groups' in artist_info:
		for group in artist_info['groups']:
			all_releases.update(find_releases(group['id']))

	if 'aliases' in artist_info:
		for alias in artist_info['aliases']:
			all_releases.update(find_releases(alias['id']))
			alias_info = find_artist_info(alias['id'])
			if 'groups' in alias_info:
				for group in alias_info['groups']:
					all_releases.update(find_releases(group['id']))

	if DEBUG:
		print(json.dumps(all_releases, indent=2))
		print(len(all_releases))

	all_releases = sorted(all_releases.values(), key=lambda x: x['year'] if 'year' in x else 3000)

	return stats(artist_info['name'], all_releases) + disco_table(all_releases)

#
# Main Program
#
if __name__ == '__main__':
	if (len(sys.argv) < 2):
		print("Usage: python "+sys.argv[0]+" [artist name] > outfile.html")
		exit()

	get_discography(sys.argv[1])