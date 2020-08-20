import socketio

# Simple class to test the socket

class MyCustomNamespace(socketio.ClientNamespace):
    def on_connect(self):
        print("connected!")
        self.emit("get", "Porya Hatami")

    def on_disconnect(self):
        print("disconnected!")

    def on_release_rows(self, data):
        print('release_rows')
        print(data)

    def on_complete(self):
        print('complete')

sio = socketio.Client(logger=True, ssl_verify=False)
sio.register_namespace(MyCustomNamespace('/discography'))
sio.connect("wss://localhost:5000", namespaces=['/discography'])
