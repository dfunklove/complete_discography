import cProfile
import sys
from .complete_discography import get_discography

# Execute the below command from outside complete_discography folder.

if (len(sys.argv) < 2):
	print("Usage: python -m complete_discography [artist name] > outfile.html")
	exit()

cProfile.run("get_discography(None, sys.argv[1])", "stats.bin")
#print(get_discography(sys.argv[1]))
