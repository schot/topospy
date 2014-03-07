topos.py
========

pythonic ToPoS library

Usage
-----

Process all available tokens in a pool:

    >>> from topos import Server
    >>> topos = Server()
    >>> pool  = topos['12345']
    >>> for token in pool:
    >>>     # do work
    >>>     pool.remove(token)

Tokens are provided as a Python dictionary with the following fields:

    {
      'id': '<>',
      'data': '<>',
      'lock': '<>',
    }

Token locking (for exclusive tokens) and lock refreshing are handled
automatically by the library if you ask for it:

    >>> pool = topos['12345']
    >>> pool.set(timeout=3600, autorefresh=True)

The lock will be removed when the token is deleted or after calling
`pool.unlock(token)`.

See `pydoc topos` for the full documentation.

Installation
------------

topos.py requires Python 2.6 or later and the [Requests][1] module.

[1]: http://docs.python-requests.org

Authors
-------

 * Jeroen Schot <jeroen.schot@surfsara.nl>

License
-------

Copyright 2014 Jeroen Schot

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

<http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
