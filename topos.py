# Copyright 2014 Jeroen Schot
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests

DEFAULT_SERVER = 'https://topos.grid.sara.nl/4.1'

class Server:

    _server = None

    def __init__(self, server=DEFAULT_SERVER):
        self._server = server

    def __getitem__(self, pool):
        return Pool(pool=pool, server=self._server)

    def new_pool(self):
        r = requests.get("{}/newPool".format(self._server))
        print r.status_code
        if r.status_code != 200:
            raise RuntimeError("error getting new pool")
        pool = r.url.split('/')[-2]
        return self.__getitem__(pool)


class Pool:

    _pool = None
    _server = None
    _timeout = None
    _autorefresh = None

    def __init__(self, pool, server=DEFAULT_SERVER):
        self._server = server
        self._pool = pool

    def __iter__(self):
        return self

    def next(self):
        params = {}
        if (self._timeout > 0):
            params['timeout'] = self._timeout
        r = requests.get("{}/pools/{}/nextToken"
            .format(self._server, self._pool),
            params={'timeout': self._timeout})
        if r.status_code == 404:
            raise StopIteration
        orig_headers = r.history[0].headers
        token = {}
        token["id"] = str(r.url.split('/')[-1])
        token["data"] = r.content
        if (self._timeout > 0):
            token["lock"] = orig_headers["x-topos-lockurl"]
        return token

    def remove(self, token):
        r = requests.delete("{}/pools/{}/tokens/{}"
            .format(self._server, self._pool, token['id']))
        if r.status_code == 404:
            raise KeyError

    def set(self, timeout=0, autorefresh=False):
        self._timeout = timeout
        self._autorefresh = autorefresh

    def unlock(self, token):
        r = requests.delete(token['lock'])
