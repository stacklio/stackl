
import tornado.ioloop
import tornado.web
import tornado.websocket
import socket
import ssl
import json

class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("new connection")
        self.certificate = None#self.request.get_ssl_certificate()
        self.remote_ip = self.request.remote_ip

        print("connection has cert '{0}' and ip '{1}'".format(self.certificate, self.remote_ip))
        self.write_message("Test_Stackl_Server says Hello!")
        
    def on_message(self, message):
        
        print("message received as json:  {}".format(message))
        loaded_message = str(json.loads(message))
        print("message received as loaded message:  {}".format(loaded_message))

        reversed_msg = loaded_message[::-1]
        # Reverse Message and send it back        
        print("sending back reversed message: {}".format(reversed_msg))
        self.write_message(json.dumps(reversed_msg))
         
    def on_close(self):
        print("Connection closed")

    def check_origin(self, origin):
        return True
 

application = tornado.web.Application([
    (r'/ws', WSHandler),
])
 
 
if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    myIP = socket.gethostbyname(socket.gethostname())
    print("*** Websocket Server Started at {}**".format(myIP))
    tornado.ioloop.IOLoop.instance().start()
