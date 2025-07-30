from sabatron_tryton_rpc_client.jsonrpc import ServerPool, ServerProxy
from functools import partial


class Client():
    def __init__(self, hostname, database, username, password,
                 port=8000, language='en'):
        self.hostname = hostname
        self.database = database
        self.username = username
        self.password = password
        self.port = port
        self.language = language

    def connect(self):
        PartialProxy = partial(ServerProxy)
        parameters = {}
        session = parameters.get('session', [''])[0]
        parameters['password'] = self.password
        proxy = PartialProxy(self.hostname, self.port, self.database)
        result = proxy.common.db.login(
            self.username, parameters, self.language
        )
        session = ':'.join(map(str, [self.username] + result))
        connection = ServerPool(
            self.hostname, self.port, self.database, session=session, cache=[])
        self.connection = connection

    def call(self, name, args):
        with self.connection() as conn:
            result = getattr(conn, name)(*args)
        return result
