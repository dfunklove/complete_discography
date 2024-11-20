#!/usr/bin/env python

import logging
import sys
from complete_discography import complete_discography

if (len(sys.argv) < 3):
    usage = """
    Complete Discography
    
    usage: python {} [api user token] [artist name] > outfile.html
    parameters: 
    - api user token: user token for the Discogs API
    - artist name: name of artist to search on
    
    Query discogs.com for list of every album on which this artist has appeared.
    Output is an HTML table.
    """
    print(usage.format(__file__))
    exit()

logging.basicConfig(filename='disco.log', level=logging.INFO, format='[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s')
print(complete_discography.get_discography(sys.argv[1], sys.argv[2]))
