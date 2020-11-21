#!/usr/bin/env python

import argparse
from complete_discography import flask_app

if __name__ == '__main__':
  usage = """
Provide a websocket interface for discography information.
The server runs securely over wss and therefore requires a certificate file and a private key file.
"""
  parser = argparse.ArgumentParser(description="Complete Discography Server", usage=usage)
  parser.add_argument('-c', '--certfile', help="server certificate file", required=True)
  parser.add_argument('-k', '--keyfile', help="private key file", required=True)
  parser.add_argument('-p', '--port', default=5000, type=int)
  args = parser.parse_args()
  
  print("Starting Complete Discography Server")
  flask_app.main(args.certfile, args.keyfile, args.port)