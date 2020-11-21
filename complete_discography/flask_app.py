# activate eventlet
import eventlet
eventlet.monkey_patch()

import sys
from os import path
from flask import Flask, make_response, request 
from flask_socketio import SocketIO, Namespace, emit
from complete_discography import complete_discography

"""
Start up a SocketIO (augmented websockets) server on port 5000
Requires a certfile and keyfile to run securely using wss protocol.
"""

app = Flask(__name__) 
app.secret_key = '7777777'
socketio = SocketIO(app, cors_allowed_origins="*")

class Discography(Namespace):
  """
  Provide a websocket interface to complete_discography.py
  When a "get" event is received, run get_discography in the background.
  Pass in self so the bg task can call publish_release_rows and publish_complete.
  This enables publishing results incrementally, one row at a time, rather than
  waiting for the entire table.
  """
  def on_get(self, artist_name):
    socketio.start_background_task(complete_discography.get_discography, artist_name, self)

  # Callbacks used by get_discography
  def publish_release_rows(self, rows):
    self.emit("release_rows", rows)

  def publish_complete(self):
    self.emit("complete")

socketio.on_namespace(Discography('/discography'))
  
def main(certfile=None, keyfile=None, port=5000):
  if (certfile and keyfile):
    if (not path.exists(certfile)):
      sys.exit("File not found: "+certfile)
    elif (not path.exists(keyfile)):
      sys.exit("File not found: "+keyfile)
    socketio.run(app, certfile=certfile, keyfile=keyfile, port=port)
  else:
    socketio.run(app, port=port)
