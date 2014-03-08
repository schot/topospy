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

    def __init__(self, server=DEFAULT_SERVER):
        self.server = server

    def __getitem__(self, pool):
        """Return a Pool object with the given pool name."""
        return Pool(pool=pool, server=self.server)

    def new_pool(self):
        """Request a new pool from the server."""
        r = requests.get("{}/newPool".format(self.server))
        if r.status_code != 200:
            raise RuntimeError("error getting new pool")
        pool = r.url.split('/')[-2]
        return self[pool]


class Pool:

    def __init__(self, pool, server=DEFAULT_SERVER):
        self.server = server
        self.pool = pool
        timeout = 0
        autorefresh = False

    def __iter__(self):
        return self

    def next(self):
        """Fetch a new token."""
        params = {}
        if (self.timeout > 0):
            params['timeout'] = self.timeout
        r = requests.get("{}/pools/{}/nextToken"
            .format(self.server, self.pool),
            params={'timeout': self.timeout})
        if r.status_code == 404:
            raise StopIteration
        orig_headers = r.history[0].headers
        token = {}
        token["id"] = r.url.split('/')[-1]
        token["data"] = r.content
        if (self.timeout > 0):
            token["lock"] = orig_headers["x-topos-lockurl"]
        return token

    def remove(self, token):
        """Remove token from the pool."""
        r = requests.delete("{}/pools/{}/tokens/{}"
            .format(self.server, self.pool, token['id']))
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
        self.timeout = timeout
        self.autorefresh = autorefresh

    def unlock(self, token):
        """Unlock token, allowing others to process it."""
        r = requests.delete(token['lock'])
