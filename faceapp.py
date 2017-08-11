import json
import string
import random
import multipart_httplib
import argparse

DEBUG = 0
USER_AGENT = "FaceApp/1.0.342 (Linux; Android 4.4)"
API = "v2.3"
HOST = "node-01.faceapp.io"

def generate_rand_id(choice, length):
    return ''.join([random.choice(choice) for x in range(length)])

class FaceAppDevice:
    def __init__(self, device_id=None, user_agent=USER_AGENT, host=HOST, api=API):
        if not device_id:
            device_id = generate_rand_id(string.ascii_lowercase, 8)
        self.device_id = device_id
        self.user_agent = user_agent
        self.host = host
        self.api = api
        self.h = multipart_httplib.MultipartHTTPSConnection(self.host)
        self.h.set_debuglevel(DEBUG)
        self.headers = {"User-Agent": self.user_agent, 
                        "X-FaceApp-DeviceID": self.device_id}

    def upload_photo(self, f):
        r = self.h.multipart_request("POST", "/api/%s/photos" % self.api, 
                                      (('name="file"; filename="image.jpg"',
                                       f.read()),), self.headers)

        return json.loads(r.read())['code']

    def filter_photo(self, photoid, filtername):
        self.h.request("GET", "/api/%s/photos/%s/filters/%s?cropped=true" % (self.api, photoid, filtername), headers = self.headers)
        r = self.h.getresponse()
        
        if r.status != 200:
            r.read()
            raise Exception(r.getheader("X-FaceApp-ErrorCode","unknown"))

        return r

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Faceapp interface.')
    parser.add_argument('filter', help="name of filter")
    parser.add_argument('infile', help="input file")
    parser.add_argument('outfile', help="destination file")

    args = parser.parse_args()

    f = FaceAppDevice()
    photoid = f.upload_photo(file(args.infile))
    file(args.outfile,"wc").write(f.filter_photo(photoid, args.filter).read())
