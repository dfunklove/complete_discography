import sys
from .complete_discography import get_discography

# Execute the below command from outside complete_discography folder.

if (len(sys.argv) < 2):
	print("Usage: python -m complete_discography [artist name] > outfile.html")
	exit()

print(get_discography(None, sys.argv[1]))
