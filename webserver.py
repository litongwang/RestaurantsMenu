from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import cgi

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

class WebserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                restaurants = session.query(Restaurant).all()
                output = ""
                output += "<a href='/restaurants/new'>Make a New Restaurant Here</a></br></br>"
                output += "<html><body><h2>"
                for restaurant in restaurants:
                    output += restaurant.name
                    output += "</br>"
                    output += "<a href='restaurants/%s/edit'>Edit</a>" % restaurant.id
                    output += "</br>"
                    output += "<a href='restaurants/%s/delete'>Delete</a>" % restaurant.id
                    output += "</br></br></br>"
                output += "</h2></body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Make a new restaurant!</h1>"
                output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>"
                output += "<input name='newRestaurantName' type='text' placeholder='Enter New Restaurant Name Here'>"
                output += "<input type='submit' value='Create'>"
                output += "</form></body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/edit"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                restaurant_id = self.path.split("/")[2]
                output = ""
                output += "<html><body>"
                output += "<h1>Enter new name!</h1>"
                output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>" % restaurant_id
                output += "<input name='newRestaurantName' type='text' placeholder='Enter New Restaurant Name Here'>"
                output += "<input type='submit' value='Rename'>"
                output += "</form></body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/delete"):
                restaurant_id = self.path.split("/")[2]
                restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
                if restaurant != []:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output += "<h1>Are you sure to delete %s ?</h1>" % restaurant.name
                    output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/delete'>" % restaurant_id
                    output += "<input type='submit' value='Delete'>"
                    output += "</form>"
                    output += "</html></body>"
                    self.wfile.write(output)

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')
                    newRestaurant = Restaurant(name=messagecontent[0])
                    session.add(newRestaurant)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')
                    restaurant_id = self.path.split("/")[2]
                    update_query = session.query(Restaurant).filter_by(
                        id=restaurant_id).one()
                    if update_query != []:
                        update_query.name = messagecontent[0]
                        session.add(update_query)
                        session.commit()
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()

            if self.path.endswith("/delete"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')
                    restaurant_id = self.path.split("/")[2]
                    delete_query = session.query(Restaurant).filter_by(id=restaurant_id).one()
                    if delete_query != []:
                        session.delete(delete_query)
                        session.commit()
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()

        except:
            pass

def main():
    try:
        server_address = ('', 8080)
        server = HTTPServer(server_address, WebserverHandler)
        print 'web server running on port 8080'
        server.serve_forever()
    except KeyboardInterrupt:
        print 'keyboard interrupt!'
        server.socket.close()

if __name__ == '__main__':
    main()
