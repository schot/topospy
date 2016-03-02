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
import socket
from threading import Event, Thread

DEFAULT_ROOT = 'https://topos.grid.sara.nl/4.1'

class Server:
    """Represents a ToPoS server instance. Only used to create Pool objects."""

    def __init__(self, root=DEFAULT_ROOT):
        self.root = root

    def __getitem__(self, pool):
        """Return a Pool object with the given pool name."""
        return Pool(name=pool, root=self.root)

    def new_pool(self):
        """Request a new pool from the server."""
        r = requests.get('{}/newPool'.format(self.root))
        if r.status_code != 200:
            raise RuntimeError('error getting new pool')
        pool = r.url.split('/')[-2]
        return self[pool]


class Pool:
    """A ToPoS token pool."""

    def __init__(self, name, root=DEFAULT_ROOT):
        self.root = root
        self.name = name
        self.timeout = 0
        self.autorefresh = False
        self.refresher = None

    def __iter__(self):
        return self

    def __next__(self):
        """Fetch a new token."""
        params = {}
        if self.timeout > 0:
            params['timeout'] = self.timeout
            params['description'] = socket.gethostname()
        r = requests.get('{}/pools/{}/nextToken'
            .format(self.root, self.name), params=params)
        if r.status_code == 404:
            raise StopIteration
        orig_headers = r.history[0].headers
        token = {}
        token['id'] = r.url.split('/')[-1]
        token['data'] = r.text
        if self.timeout > 0:
            token['lock'] = orig_headers['x-topos-lockurl']
        if 'lock' in token and self.autorefresh:
            self.refresher.add(token['lock'], self.timeout)
        return token

    def next(self):
        return self.__next__()

    def remove(self, token):
        """Remove token from the pool."""
        if 'lock' in token and self.autorefresh:
            self.refresher.remove(token['lock'])
        r = requests.delete('{}/pools/{}/tokens/{}'
            .format(self.root, self.name, token['id']))
        if r.status_code == 404:
            raise KeyError

    def set(self, timeout=0, autorefresh=False):
        """Set optional properties of this pool.

        Keyword arguments:
         * timeout -- time in seconds after which token locks will expire
         * autorefresh -- if True locks will be refreshed until the
                          corresponding token is deleted or unlocked
        """
        self.timeout = timeout
        self.autorefresh = autorefresh
        if autorefresh:
            self.refresher = Refresher()

    def unlock(self, token):
        """Unlock token, allowing others to process it."""
        if 'lock' in token and self.autorefresh:
            self.refresher.remove(token['lock'])
        requests.delete(token['lock'])


class Refresher:
    """Continuously refreshes locks until unlocked or deleted."""

    def __init__(self):
        self.locks = {}

    def add(self, lock, timeout):
        """Add the lock to the set of locks that are autorefreshed."""
        event = Event()
        self.locks[lock] = event
        t = Thread(target=refresh_lock, args=(event, lock, timeout))
        t.setDaemon(True)
        t.start()

    def remove(self, lock):
        """Stop refreshing the given lock."""
        if lock in self.locks:
            self.locks[lock].set()
            del self.locks[lock]


def refresh_lock(stop, lock, timeout):
    """Keep refreshing the lock until the stop event received."""
    waittime = max(5.0, timeout/2.0 - 10.0)
    while not stop.wait(waittime):
        requests.get(lock, params={'timeout': timeout})
