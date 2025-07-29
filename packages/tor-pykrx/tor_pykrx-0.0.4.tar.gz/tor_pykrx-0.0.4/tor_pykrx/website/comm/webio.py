from abc import abstractmethod
from tor_request.clients import RequestsClient

class Get:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "http://data.krx.co.kr/"
        }
        self.rc = RequestsClient()

    def read(self, **params):
        resp = self.rc.request_with_retry(url=self.url, headers=self.headers, params=params)
        return resp

    @property
    @abstractmethod
    def url(self):
        return NotImplementedError

class Post:
    def __init__(self, headers=None):
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "http://data.krx.co.kr/"
        }
        if headers is not None:
            self.headers.update(headers)

        self.rc = RequestsClient()

    def read(self, **params):
        resp = self.rc.request_with_retry(url=self.url, method="post", headers=self.headers, data=params)
        return resp

    @property
    @abstractmethod
    def url(self):
        return NotImplementedError
