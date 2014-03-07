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

"""pythonic ToPoS library"""

import requests

DEFAULT_SERVER = 'https://topos.grid.sara.nl/4.1'

class Server:
    """Represents a ToPoS server instance. Only used to create Pool objects."""
    _server = None

    def __init__(self, server=DEFAULT_SERVER):
        self._server = server

    def __getitem__(self, pool):
        """Return a Pool object with the given pool name."""
        return Pool(pool=pool, server=self._server)

    def new_pool(self):
        """Request a new pool from the server."""
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
        """Fetch a new token."""
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
        """Remove token from the pool."""
        r = requests.delete("{}/pools/{}/tokens/{}"
            .format(self._server, self._pool, token['id']))
        if r.status_code == 404:
            raise KeyError

    def set(self, timeout=0, autorefresh=False):
        """Set optional properties of this pool.

        Keyword arguments:
        timeout -- time in seconds after which token locks will expire
        autorefresh -- if True locks will be refreshed until the
                       corresponding token is deleted or unlocked
                       (not yet implemented)
        """
        self._timeout = timeout
        self._autorefresh = autorefresh

    def unlock(self, token):
        """Unlock token, allowing others to process it."""
        r = requests.delete(token['lock'])
