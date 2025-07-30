from tryton_rpc_client.client import Client

client = Client(hostname='localhost', database='tryton', username='admin',
                password='admin')

client.connect()

name = 'model.party.party.read'
args = ([1], ['id', 'name', 'code'], {})

print(client.call(name, args))
