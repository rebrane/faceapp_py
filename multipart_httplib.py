import httplib
import random

def generate_rand_id(choice, length):
    return ''.join([random.choice(choice) for x in range(length)])

class MultipartHTTPResponse(httplib.HTTPResponse, object):
    # Override the 'begin' method to consume the 100 continue
    def begin(self):
        self.will_close = 0
        self._read_status()
        self.fp.readline()

class MultipartHTTPSConnection(httplib.HTTPSConnection):
    def multipart_request(self, method, url, params, headers={}):
        boundary = "-"*24 + generate_rand_id("0123456789abcdef", 16)

        print "making data"
        i=0
        data = []
        for p in params:
            data.append("--" + boundary + "\r\n" +
                        "Content-Disposition: form-data; " + p[0] + "\r\n\r\n" +
                        p[1] + "\r\n")
            i=i+1
            print "added data ",i
        data.append("--" + boundary + "--\r\n")
        body = ''.join(data)

        self.putrequest(method, url)
        for h in headers:
            self.putheader(h, headers[h])
        self.putheader("Content-Length", str(len(body)))
        self.putheader("Expect", "100-continue")
        self.putheader("Content-Type", "multipart/form-data; boundary=%s" % \
                                    boundary)
        self.endheaders()

        self.response_class = MultipartHTTPResponse
        r = self.getresponse()
        self.response_class = httplib.HTTPResponse

        self.send(body)

        super(MultipartHTTPResponse, r).begin()

        return r
