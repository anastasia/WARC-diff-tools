import os
import urlparse
import warc
from httplib import HTTPResponse
from StringIO import StringIO
import zlib
import simhash
from bs4 import BeautifulSoup

class FakeSocket():
    def __init__(self, response_str):
        self._file = StringIO(response_str)
    def makefile(self, *args, **kwargs):
        return self._file

def html_to_text(html_str):
    soup = BeautifulSoup(html_str, "html.parser")
    [s.extract() for s in soup('script')]
    return soup.body.getText()

def get_simhash_distance(str_one, str_two):
    try:
        res = simhash.Simhash(str_one).distance(simhash.Simhash(str_two))
    except:
        res = None
        pass
    finally:
        return res

def warc_to_dict(warc_filename):
    # TODO: check if stream
    warc_open = warc.open(warc_filename)
    response = {}

    for record in warc_open:
        payload = decompress_payload(record.payload.read(), record.type, record.url)

        if record.type in response:
            if record.url in response[record.type]:
                response[record.type][record.url].append(payload)
            else:
                response[record.type][record.url] = [payload]
        else:
            response[record.type] = {record.url:[payload]}

def decompress_payload(payload, record_type, record_url):
    try:
        source = FakeSocket(payload)
        res = HTTPResponse(source)
        res.begin()
        result = zlib.decompress(res.read(), 16+zlib.MAX_WBITS)
    except Exception as e:
        # print record_type, record_url
        result = payload
        # try:
        #     result = '.'.join(str(ord(c)) for c in payload)
        # except:
        #     result = payload
    return result

def sort_resources(collection_one, collection_two):
    """
    sorting dictionaries of collections into:
        - missing (no longer available),
        - added (newly added since first capture), and
        - common (seen in both)
    """

    missing_resources, added_resources, common_resources = dict(), dict(), dict()

    for key in collection_one.keys():
        set_a = set(collection_one[key])
        set_b = set(collection_two[key])
        common_resources[key] = list(set_a & set_b)
        missing_resources[key] = list(set_a - set_b)
        added_resources[key] = list(set_b - set_a)

    return (missing_resources, added_resources, common_resources)


def get_warc_parts(warc_path, submitted_url):
    warc_open = warc.open(warc_path)
    response_urls = {}
    for record in warc_open:
        if record.type == 'response':
            path = urlparse.urlparse(record.url).path
            ext = os.path.splitext(path)[1]
            if ext in response_urls:
                response_urls[ext].append(record.url)
            else:
                response_urls[ext] = [record.url]

            if record.url == submitted_url:
                payload = decompress_payload(record.payload.read(), 'response', record.url)
    return payload, response_urls
