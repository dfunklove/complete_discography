import sys
from .complete_discography import get_discography

# Execute the below command from outside complete_discography folder.

if (len(sys.argv) < 2):
	print("Usage: python -m complete_discography [discogs artist id] > outfile.html")
	print("(Must obtain artist id from discogs.com.  Look up an artist and the id will be in the url.)")
	exit()

print(get_discography(sys.argv[1]))
