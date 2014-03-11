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

Tokens are provided as a Python dictionary with the following fields::

  {
    'id':   '...',
    'data': '...',
    'lock': '...',
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

topos.py requires Python 2.7 or later and the Requests_ module.

.. _Requests: http://docs.python-requests.org/

Authors
-------

- Jeroen Schot <jeroen.schot@surfsara.nl>

License
-------

This software is licenced under the Apache License, Version 2.0. See the
accompanying LICENSE file for details.
