# activate eventlet
import eventlet
eventlet.monkey_patch()

from flask import Flask, make_response, request 
from flask_socketio import SocketIO, Namespace, emit
from complete_discography import get_discography
  
app = Flask(__name__) 
app.secret_key = '7777777'
socketio = SocketIO(app, cors_allowed_origins="*")

class Discography(Namespace):
  def on_get(self, artist_name):
    socketio.start_background_task(get_discography, artist_name, self)

  # Callbacks used by get_discography
  def publish_release_rows(self, rows):
    self.emit("release_rows", rows)

  def publish_empty_result(self):
    self.emit("empty_result")

socketio.on_namespace(Discography('/discography'))
  
if __name__ == '__main__':   
    socketio.run(app) 
