import sys
import time
import json
import BaseHTTPServer
import threading
import faceapp
import collections
import re
import faceapp
import urllib
import slackbot
import traceback
import params

server_shutdown = threading.Event()
server_sem = threading.Semaphore(0)
msg_queue = collections.deque()
slack = slackbot.Slackbot(params.token, params.channel)

class SlackRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	server_version = "SlackBotHTTP/" + "0.1"
	def do_POST(self):
		global msg_queue,server_sem
		r = json.loads(
			self.rfile.read(int(self.headers["Content-Length"])))

		if r["token"] != params.id_token:
			self.send_response(400)
			return

		msg_queue.appendleft(r)
		server_sem.release()

		self.send_response(200)
		self.end_headers()
		
def run(server_class=BaseHTTPServer.HTTPServer,
	    handler_class=SlackRequestHandler):
    server_address = ('127.0.0.1', 8889)
    httpd = BaseHTTPServer.HTTPServer(server_address, SlackRequestHandler)
    httpd.timeout = 1
    while not server_shutdown.is_set():
	    httpd.handle_request()

faceapp = faceapp.FaceAppDevice()

def faceapp_filter(args, channel):
    (fname, url) = args
    f = urllib.urlopen(url)
    key = faceapp.upload_photo(f)
    slack.upload_file(faceapp.filter_photo(key,fname), str(channel))

handlers = ((re.compile("!faceapp\s+(\S+)\s+<(http\S+)>"), faceapp_filter),
            (re.compile("!(female)\s+<(http\S+)>"), faceapp_filter),
            (re.compile("!(male)\s+<(http\S+)>"), faceapp_filter),
            (re.compile("!(hot)\s+<(http\S+)>"), faceapp_filter),
            (re.compile("!(young)\s+<(http\S+)>"), faceapp_filter),
            (re.compile("!(old)\s+<(http\S+)>"), faceapp_filter))

def process(d):
    for h in handlers:
        try:
            m = h[0].match(d["event"]["text"])
        except KeyError:
            return
        if m:
            try:
                h[1](m.groups(), d["event"]["channel"])
                return
            except Exception, e:
                slack.post_message(e, d["event"]["channel"])
                traceback.print_exc()
    print "no match for", d["event"]["text"]

if __name__ == "__main__":
    server = threading.Thread(target=run)
    server.start()
    try:
        while True:
            if server_sem.acquire(False):
                r = msg_queue.pop()
                #print json.dumps(r, sort_keys=True,indent=4, separators=(',', ': '))
                process(r)
            else:
                time.sleep(0.1)
    except KeyboardInterrupt:
        server_shutdown.set()
        print "bye"
        server.join()
        sys.exit()
