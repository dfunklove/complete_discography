import socketio

# A simple client to test the websocket server.

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

if __name__ == "__main__":
    sio = socketio.Client(logger=True, ssl_verify=False)
    sio.register_namespace(MyCustomNamespace('/discography'))
    sio.connect("wss://localhost:5000", namespaces=['/discography'])
