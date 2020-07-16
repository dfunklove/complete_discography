import requests
import json

"""
requests_with_caching.py

Cache HTTP requests in a text file in the local directory.  See "get" function for more info.

Adapted from <a href="https://fopp.umsi.education/books/published/fopp/index.html">Foundations of Python Programming</a>,
an online course from UMSI, specifically chapter 24, "Internet APIs".
This chapter can be unlocked by accessing the above online book through the course 
"Data Collection and Processing with Python" on Coursera, also by UMSI.
Updated by Daniel Lovette for compatibility with Python 3.6.9
"""

PERMANENT_CACHE_FNAME = "permanent_cache.txt"
TEMP_CACHE_FNAME = "this_page_cache.txt"

class Response:
    "A stub which holds just enough data to emulate requests.Response for the needs of this program."

    def __init__(self, text, url):
        self.text = text
        self.url = url


def _write_to_file(cache, fname):
    with open(fname, 'w') as outfile:
        outfile.write(json.dumps(cache, indent=2))

def _read_from_file(fname):
    try:
        with open(fname, 'r') as infile:
            res = infile.read()
            return json.loads(res)
    except:
        return {}

def add_to_cache(cache_file, cache_key, cache_value):
    temp_cache = _read_from_file(cache_file)
    temp_cache[cache_key] = cache_value
    _write_to_file(temp_cache, cache_file)

def clear_cache(cache_file=TEMP_CACHE_FNAME):
    _write_to_file({}, cache_file)

def make_cache_key(baseurl, params_d, private_keys=["api_key"]):
    """Makes a long string representing the query.
    Alphabetize the keys from the params dictionary so we get the same order each time.
    Omit keys with private info."""
    alphabetized_keys = sorted(params_d.keys())
    res = []
    for k in alphabetized_keys:
        if k not in private_keys:
            res.append("{}-{}".format(k, params_d[k]))
    return baseurl + "_".join(res)

def get(baseurl, params={}, private_keys_to_ignore=["api_key"], permanent_cache_file=PERMANENT_CACHE_FNAME, temp_cache_file=TEMP_CACHE_FNAME):
    """
    Return a Response object (defined in this file) for the given URL.  
    Look in temp_cache first, then permanent_cache.
    If not found, fetch data from the internet.
    """
    full_url = requests.Request("GET", baseurl, params).prepare().url
    cache_key = make_cache_key(baseurl, params, private_keys_to_ignore)
    # Load the permanent and page-specific caches from files
    permanent_cache = _read_from_file(permanent_cache_file)
    temp_cache = _read_from_file(temp_cache_file)
    if cache_key in temp_cache:
        #print("found in temp_cache")
        # make a Response object containing text from the change, and the full_url that would have been fetched
        return Response(temp_cache[cache_key], full_url)
    elif cache_key in permanent_cache:
        #print("found in permanent_cache")
        # make a Response object containing text from the change, and the full_url that would have been fetched
        return Response(permanent_cache[cache_key], full_url)
    else:
        #print("new; adding to cache")
        # actually request it
        resp = requests.get(baseurl, params)
        # save it
        add_to_cache(temp_cache_file, cache_key, resp.text)
        return resp