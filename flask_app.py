from flask import Flask, make_response, request 
from flask_restful import Resource, Api 
from .complete_discography import get_discography
  
app = Flask(__name__) 
api = Api(app) 
  
class Discography(Resource):
  def get(self, name):
    return make_response(get_discography(name))
  
api.add_resource(Discography, '/discography/<string:name>')
  
if __name__ == '__main__':   
    app.run(debug = True) 
