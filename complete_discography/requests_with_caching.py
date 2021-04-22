import requests
import json
from time import ctime

"""
requests_with_caching.py

Cache HTTP requests in a text file in the local directory.  See "get" function for more info.
Caching is relatively slow, disk intensive, and not thread safe.
This is intended for development, to reduce repetetive API requests and improve execution time.
When deploying to production, set DISABLE_CACHING to True.

Adapted from <a href="https://fopp.umsi.education/books/published/fopp/index.html">Foundations of Python Programming</a>,
an online course from UMSI, specifically chapter 24, "Internet APIs".
This chapter can be unlocked by accessing the above online book through the course 
"Data Collection and Processing with Python" on Coursera, also by UMSI.
Updated by Daniel Lovette for compatibility with Python 3.6.9
"""

PERMANENT_CACHE_FNAME = "/tmp/permanent_cache.txt"
TEMP_CACHE_FNAME = "/tmp/this_page_cache.txt"
DEBUG = True
DISABLE_CACHING = True

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

def make_cache_key(baseurl, params_d, private_keys=[]):
    """Makes a long string representing the query.
    Alphabetize the keys from the params dictionary so we get the same order each time.
    Omit keys with private info."""
    alphabetized_keys = sorted(params_d.keys())
    res = []
    for k in alphabetized_keys:
        if k not in private_keys:
            res.append("{}-{}".format(k, params_d[k]))
    return baseurl + "_".join(res)

def get(baseurl, params=None, headers=None, private_keys_to_ignore=["key", "secret"], permanent_cache_file=PERMANENT_CACHE_FNAME, temp_cache_file=TEMP_CACHE_FNAME):
    """
    Return a Response object (defined in this file) for the given URL.  
    Look in temp_cache first, then permanent_cache.
    If not found, fetch data from the internet.
    """

    if params == None:
        params = {}
    for k in params:
        params[k] = str(params[k])
    if headers == None:
        headers = {}
    if "user-agent" not in headers: # avoid captcha
        headers["user-agent"] = "Lynx/2.9.0dev.5 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/3.6.13"

    cache_key = make_cache_key(baseurl, params, private_keys_to_ignore)

    full_url = requests.Request("GET", baseurl, params=params, headers=headers).prepare().url
    if DEBUG:
        print(ctime() + ": fetching " + full_url)

    if not DISABLE_CACHING:

        # Load the permanent and page-specific caches from files
        permanent_cache = _read_from_file(permanent_cache_file)
        temp_cache = _read_from_file(temp_cache_file)
        if cache_key in temp_cache:
            if DEBUG:
                print("found in temp_cache")
            # make a Response object containing text from the change, and the full_url that would have been fetched
            return Response(temp_cache[cache_key], full_url)
        elif cache_key in permanent_cache:
            if DEBUG:
                print("found in permanent_cache")
            # make a Response object containing text from the change, and the full_url that would have been fetched
            return Response(permanent_cache[cache_key], full_url)

    if DEBUG:
        print("new; adding to cache")
    # actually request it
    resp = requests.get(baseurl, params=params, headers=headers)
    # save it
    if resp.status_code == requests.codes.ok:
        add_to_cache(temp_cache_file, cache_key, resp.text)
    elif DEBUG:
        print(f"not adding due to error code {resp.status_code}")
    return resp
