.. _README:

Python Tryton RPC Client
========================

Allow connect to Tryton Server using RPC.

It code is based and extracted from tryton package but removing gtk calls.

Install
-------

.. code-block:: bash

   pip install sabatron-tryton-rpc-client

Use
---

.. code-block:: python

  from sabatron_tryton_rpc_client.client import Client

  client = Client(hostname='localhost', database='tryton', username='admin',
                password='admin')
  client.connect()
  
  name = 'model.party.party.read'
  args = ([1], ['id', 'name', 'code'], {})
  
  print(client.call(name, args))
  # [{'id': 1, 'name': 'Empresa', 'code': '1'}]

Licence
-------

GNU General Public License (GPL) (GPL-3) 
