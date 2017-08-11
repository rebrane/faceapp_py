import json
import string
import random
import httplib

DEBUG=1

def generate_device_id():
    return ''.join([random.choice(string.ascii_lowercase) for x in range(8)])

USER_AGENT = "FaceApp/1.0.342 (Linux; Android 4.4)"

class UploadHTTPResponse(httplib.HTTPResponse, object):
    # Override the 'begin' method to consume the 100 continue
    def begin(self):
        self.will_close = 0
        self._read_status()
        self.fp.readline()

class FaceAppDevice:
    def __init__(self,
             device_id=None, 
             user_agent=USER_AGENT,
             host="node-01.faceapp.io",
             api="v2.3"):
        if not device_id:
            device_id = generate_device_id()
        self.device_id = device_id
        self.user_agent = user_agent
        self.host = host
        self.api = api
        self.h = httplib.HTTPConnection(self.host)
        self.h.set_debuglevel(DEBUG)
        self.headers = (("User-Agent", self.user_agent),
                        ("X-FaceApp-DeviceID",self.device_id))

    def upload_photo(self, filename):
        boundary = "-"*24 + ''.join([random.choice('0123456789abcdef') for x in range(16)])
        data = "--" + boundary + "\r\n" + \
               'Content-Disposition: form-data; name="file"; filename="image.jpg"\r\n\r\n' + \
               file(filename).read() + \
               "\r\n--" + boundary + "--\r\n"

        self.h.putrequest("POST", "/api/%s/photos" % self.api)
        for hd in self.headers:
            self.h.putheader(*hd)
        self.h.putheader("Content-Length", str(len(data)))
        self.h.putheader("Expect", "100-continue")
        self.h.putheader("Content-Type", "multipart/form-data; boundary=%s" % \
                                    boundary)
        self.h.endheaders()
        self.h.response_class = UploadHTTPResponse
        r = self.h.getresponse()
        x=self.h.debuglevel
        self.h.set_debuglevel(0)
        self.h.send(data)
        self.h.set_debuglevel(x)
        # Now get the real response
        super(UploadHTTPResponse, r).begin()

        if r.status != 200:
            raise Exception(response.getheader("X-FaceApp-ErrorCode","unknown"))

        return json.loads(r.read())

    def filter_photo(self, photoid, filtername):
        self.h.putrequest("GET", "/api/%s/photos/%s/filters/%s?cropped=false" % (self.api, photoid, filtername))
        for hd in self.headers:
            self.h.putheader(*hd)
        self.h.endheaders()
        self.h.response_class = httplib.HTTPResponse
        r = self.h.getresponse()
        
        if r.status != 200:
            raise Exception(r.getheader("X-FaceApp-ErrorCode","unknown"))

        return r.read()
