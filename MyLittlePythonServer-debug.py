from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from CGIHTTPServer import CGIHTTPRequestHandler
from os import curdir, sep
from SocketServer import ThreadingMixIn
import cgi
import mimetypes
import os
import socket
import sys
import threading
import time
import urlparse

mimetypes.init()
mimetypes.knownfiles

if sys.argv[1:]:
    bind = sys.argv[1]
else:
    bind = '127.0.0.1'

if sys.argv[2:]:
    port = int(sys.argv[2])
else:
    port = 8080

class Handler(CGIHTTPRequestHandler):

    CGIHTTPRequestHandler.cgi_directories = ["/www/cgi-bin"]
    CGIHTTPRequestHandler.protocol_version = "HTTP/1.1"
    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        message_parts = [
                'CLIENT VALUES:',
                'client_address=%s (%s)' % (self.client_address,
                                            self.address_string()),
                'command=%s' % self.command,
                'path=%s' % self.path,
                'real path=%s' % parsed_path.path,
                'query=%s' % parsed_path.query,
                'request_version=%s' % self.request_version,
                '',
                'SERVER VALUES:',
                'server_version=%s' % self.server_version,
                'sys_version=%s' % self.sys_version,
                'protocol_version=%s' % self.protocol_version,
                '',
                'HEADERS RECEIVED:',
                ]
        for name, value in sorted(self.headers.items()):
            message_parts.append('%s=%s' % (name, value.rstrip()))
        message_parts.append('')
        message = '\r\n'.join(message_parts)
        threadmessage = threading.currentThread().getName()
        #self.send_response(200)
        #self.send_header("Content-type", "text/html")
        #self.send_header('Last-Modified', self.date_time_string(time.time()))
        #self.end_headers()
        #print(self.wfile)
        #self.wfile.write(message)
        #self.wfile.write('Response body\n')
        #self.wfile.write("<html><head><title>Python Test Server</title></head>")
        #self.wfile.write("<body><p>This is a test.</p>")
        # If someone went to "http://something/foo/bar/",
        # then s.path equals "/foo/bar/".
        #self.wfile.write("<p>You accessed path: %s</p>" % self.path)
        #self.wfile.write("</body>")
        #self.wfile.write(message)
        #self.wfile.write(threadmessage)
        #self.wfile.write(os.listdir(self.path))
        #self.wfile.write("</html>")
        #self.wfile.close()
        if self.path=="/":
            self.path="/index.html"

        try:
            #Check the file extension required and
            #set the right mime type

            sendReply = False
            if self.path.endswith(".html"):
                mimetype='text/html'
                sendReply = True
            if self.path.endswith(".jpg"):
                mimetype='image/jpg'
                sendReply = True
            if self.path.endswith(".gif"):
                mimetype='image/gif'
                sendReply = True
            if self.path.endswith(".js"):
                mimetype='application/javascript'
                sendReply = True
            if self.path.endswith(".css"):
                mimetype='text/css'
                sendReply = True
            if self.path.endswith(".tar.gz"):
                mimetype='application/x-tar-gz'
                sendReply = True
            if self.path.endswith(".7z"):
                mimetype='application/x-7z-compressed'
                sendReply = True
            if self.path.endswith(".torrent"):
                mimetype='application/x-bittorrent'
                sendReply = True
            fileend = os.path.splitext(self.path)[1]
            print(fileend)

            if sendReply == True:
                #Open the static file requested and send it
                f = open(curdir + sep + '/www' + self.path)
                self.send_response(200)
                self.send_header('Content-type',mimetype)
                self.send_header('Last-Modified', self.date_time_string(time.time()))
                size = os.path.getsize(curdir + sep + self.path)
                if size > 0:
                    self.send_header('Content-Length', size)
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                print(size)
            return

        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)
        return

    def do_POST(self):
        # Parse the form data posted
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })

        # Begin the response
        self.send_response(200)
        self.end_headers()
        self.wfile.write('Client: %s\n' % str(self.client_address))
        self.wfile.write('User-agent: %s\n' % str(self.headers['user-agent']))
        self.wfile.write('Path: %s\n' % self.path)
        self.wfile.write('Form data:\n')

        # Echo back information about what was posted in the form
        for field in form.keys():
            field_item = form[field]
            if field_item.filename:
                # The field contains an uploaded file
                file_data = field_item.file.read()
                file_len = len(file_data)
                del file_data
                self.wfile.write('\tUploaded %s as "%s" (%d bytes)\n' % \
                        (field, field_item.filename, file_len))
            else:
                # Regular form value
                self.wfile.write('\t%s=%s\n' % (field, form[field].value))
        return

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    ipv6 = socket.AF_INET6
    ipv4 = socket.AF_INET
    if sys.argv[3:]:
        address_family = sys.argv[3]
    else:
        address_family = ipv4

if __name__ == '__main__':
    try:
        from BaseHTTPServer import HTTPServer
        server = ThreadedHTTPServer((bind, port), Handler)
        print 'Starting server, use <Ctrl-C> to stop'
        server.serve_forever()
    except KeyboardInterrupt:
        print 'Server Shutting Down By User'
        server.socket.close()