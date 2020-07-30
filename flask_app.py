from flask import Flask, make_response, request 
from flask_restful import Resource, Api 
from .complete_discography import get_artists, get_discography
  
app = Flask(__name__) 
api = Api(app) 

class Artists(Resource):
  def get(self, name):
    return make_response(get_artists(name))

class Discography(Resource):
  def get(self, artist_id):
    return make_response(get_discography(artist_id))
  
api.add_resource(Artists, '/artists/<string:name>')
api.add_resource(Discography, '/discography/<string:artist_id>')
  
if __name__ == '__main__':   
    app.run(debug = True) 
