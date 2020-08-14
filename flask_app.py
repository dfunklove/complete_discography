from flask import Flask, make_response, request 
from flask_socketio import SocketIO, Namespace, emit
from complete_discography import get_discography
  
app = Flask(__name__) 
app.secret_key = '7777777'
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, async_handlers=True)

class Discography(Namespace):
  def on_get(self, artist_name):
    socketio.start_background_task(get_discography, socketio, artist_name)

socketio.on_namespace(Discography('/discography'))
  
if __name__ == '__main__':   
    socketio.run(app, debug = True) 
