import time
import requests


class RequestError(Exception):
    def __init__(self, res):
        self.res = res
        self.message = res.text
        super().__init__(self.message)

    def __str__(self):
        return f"Reponse {self.message['status']}: {self.message['message']}"


class BaseApiObject(object):
    base_url = "https://api.henrikdev.xyz/valorant"

    def __init__(self, debug=False):
        self.debug = debug

        self.session = requests.Session()

        self.cache = {}
        self.cache_time = {}

        self.logTag = f"BaseApiObject|{self.__class__.__name__}"

    def _request(self, path, max_cache_age=10):
        if path in self.cache and max_cache_age > (time.time() - self.cache_time[path]):
            if self.debug:
                print(f"[{self.logTag}]\t_request({path}):\tUsing cached")
            return self.cache[path]
        else:
            if self.debug:
                print(f"[{self.logTag}]\t_request({path}):\tRequesting")
            r = self.session.get(f"{self.base_url}/{path}")
            if r.status_code == 200:
                j = r.json()

                self.cache_time[path] = time.time()
                self.cache[path] = j

                return j
            else:
                raise RequestError(r)

    def toggle_debug(self):
        self.debug = not self.debug
