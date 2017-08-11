import urllib
import multipart_httplib

class Slackbot(object):
    def __init__(self, token, channels):
        self.token = token
        self.h = multipart_httplib.MultipartHTTPSConnection("slack.com")
        self.channels = channels

    def upload_file(self, imgfile, channel):
        r = self.h.multipart_request("POST", "/api/files.upload",
                                      (('name="file"; filename="image.jpg"', imgfile.read()),
                                       ('name="token"', self.token),
                                       ('name="channels"', channel)))

        print r.status, r.reason
        print r.read()

    def post_message(self, msg, channel):
        params = urllib.urlencode({"token":self.token, "channel":channel, "text":msg})
        self.h.request("POST", "/api/chat.postMessage", params, {"Content-Type":"application/x-www-form-urlencoded"})
        r = self.h.getresponse()
        print r.status, r.reason
        print r.read()
