import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("<html><body><h1>Welcome to the Tornado web server!</h1></body></html>")