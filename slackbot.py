import multipart_httplib

class Slackbot(object):
    def __init__(self, token):
        self.token = token
        self.h = multipart_httplib.MultipartHTTPSConnection("slack.com")

    def upload_file(self, imgfile):
        r = self.h.multipart_request("POST", "/api/files.upload",
                                      (('name="file"; filename="image.jpg"', imgfile.read()),
                                       ('name="token"', self.token),
                                       ('name="channels"', '#womes-and-tanes')))

        print r.status, r.reason
        print r.read()
