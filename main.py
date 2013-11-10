#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import cgi
import json
import subprocess
import base64
import sys

PORT_NUMBER = 8000
USERNAME = 'user'
PASS = 'pass'

settings = {}
proc = {}

def writeSettings():
	with open('settings.json', 'w+') as outfile:
		json.dump(settings, outfile)

#This class will handles any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):
	#Handler for the GET requests

	def do_AUTHHEAD(self):
		self.send_response(401)
		self.send_header('WWW-Authenticate', 'Basic realm=\"Test\"')
		self.send_header('Content-type', 'text/html')
		self.end_headers()

	def authenticate(self):
		if self.headers.getheader('Authorization') == None:
			self.do_AUTHHEAD()
			self.wfile.write('no auth header received')
			return False
		else:
			ast = self.headers.getheader('Authorization')
			creds = base64.b64decode(ast.split()[1])
			splittedcreds = creds.split(':')
			if splittedcreds[0] == USERNAME and splittedcreds[1] == PASS:
				return True
			else:
				self.do_AUTHHEAD()
				self.wfile.write('invalid credentials')
				return False

	def do_GET(self):
		global proc

		if not self.authenticate():
			return

		if self.path=="/":
			self.path="html/index.html"
		if self.path=="/last":
			self.send_response(200)
			self.send_header('Content-type','application/json')
			self.end_headers()
			string = json.dumps(settings)
			print string
			self.wfile.write(string)
			return
		if self.path=="/status":
			running = False

			try:
				pr = proc.poll()

				if pr == None:
					running = True
			except:
				pass

			res = {'running': running}
			self.send_response(200)
			self.send_header('Content-type','application/json')
			self.end_headers()
			string = json.dumps(res)
			print string
			self.wfile.write(string)
			return

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

			if sendReply == True:
				#Open the static file requested and send it
				f = open(curdir + sep + self.path) 
				self.send_response(200)
				self.send_header('Content-type',mimetype)
				self.end_headers()
				self.wfile.write(f.read())
				f.close()
			return

		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)

	#Handler for the POST requests
	def do_POST(self):
		global settings
		global proc

		if self.path=="/start":			
			length = int(self.headers.getheader('content-length'))
			
			settings = json.loads(self.rfile.read(length))

			#
			# Split the URL into the components that httperf likes
			#
			lurl = settings['lasturl']
			if '//' in lurl:
				prefix, lurl1 = lurl.split('//',1)

			if '/' in lurl1:
				server, uri = lurl1.split('/',1)
				uri = '/' + uri
			else:
				server = lurl1
				uri = '/'

			#
			# before starting a new instance of httperf, kill the existing one(s)
			#
			try:
				proc.terminate()
			except:
				pass

			#
			# Spawn httperf
			#
			cmd = ["httperf", "--server", server, "--uri", uri, "--num-conn", "1000000000", "--num-call", "1", "--rate", settings['rate']]
			proc = subprocess.Popen(cmd)

			print 'started'

			#
			# Update the settings with the ones coming from the client
			#
			with open('settings.json', 'w+') as outfile:
				json.dump(settings, outfile)

			self.send_response(200)
			self.end_headers()
			self.wfile.write("ok")
			return
		if self.path=="/stop":
			try:
				proc.terminate()
			except:
				pass

			print "stopped"

			self.send_response(200)
			self.end_headers()
			self.wfile.write("ok")
			return			

#
# If the port is specified on the command line, use it
#
if len(sys.argv) > 1:
	PORT_NUMBER = int(sys.argv[1])
	print PORT_NUMBER

#
# Load the config
#
try:
	settings = json.loads(open('settings.json').read())
except IOError:
	settings['rate'] = 20;
	settings['conn'] = 100;
	settings['lasturl'] = '';
	settings['urls'] = {};
	writeSettings()

#
#Create a web server and define the handler to manage the
#incoming request
#
server = HTTPServer(('', PORT_NUMBER), myHandler)
print 'Started httpserver on port ' , PORT_NUMBER
	
try:
	#
	# Wait forever for incoming htto requests
	#
	server.serve_forever()

except KeyboardInterrupt:
	print '^C received, shutting down the web server'
	server.socket.close()
