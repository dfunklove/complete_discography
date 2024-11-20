import discogs_client
import logging
import traceback

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

USER_AGENT = 'complete_discography/1.0 +https://github.com/dfunklove/complete_discography'

def make_album_rows(artist, context=None):
	results = []
	for page_num in range(1, artist.releases.pages):
		results += make_album_rows_from_page(artist.releases.page(page_num), context)
	return results

def make_album_rows_from_page(page, context=None):
	"""
	Translate the data from the given page of releases into HTML table rows.
	Pass the results to the context before returning them.

	Required Parameters:
	page: a page of releases from discogs_client

	Optional Parameters:
	context: an object which has the methods publish_release_rows and publish_complete
	"""
	results = []
	for release in page:
		row = '<tr>'
		row += f"<td><a href=\"{release.data.get('resource_url')}\"><img src=\"{release.data.get('thumb')}\"></a></td>"
		row += f"<td>{release.data.get('artist')}</td>"
		row += f"<td><a href=\"{release.data.get('resource_url')}\">{release.data.get('title')}</a></td>"
		row += f"<td>{release.data.get('year')}</td>"
		row += '</tr>'
		results.append(row)
	if context and len(results) > 0:
		context.publish_release_rows(results)
	return results

def get_discography(user_token, name, context=None):
	"""
	Query discogs database to get all albums on which the given artist,  
	specified by "name", has appeared.

	Pass the results, as html table rows, to the context before returning them.

	Required Parameters:
	user_token: a user token to authenticate with the API
	name: the name of the artist to search for

	Optional Parameters:
	context: an object which has the methods publish_release_rows and publish_complete
	"""
	try:
		client = discogs_client.Client(USER_AGENT, user_token=user_token)
		artist = client.search(name, type='artist').page(1)[0]
		album_rows = make_album_rows(artist, context)

		# Find releases for groups
		for group in artist.groups:
			album_rows += make_album_rows(group, context)

		# Find releases for each alias
		for alias in artist.aliases:
			album_rows += make_album_rows(alias, context)

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