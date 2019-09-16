import tarantool
import logging

HOST = "localhost"
PORT = 33013
SOCKET_TIMEOUT = 1
RECONNECT_MAX_ATTEMPTS = 2


class Store(object):
    def __init__(self, log=True):
        self.connection = None
        self.host = HOST
        self.port = PORT
        self.socket_timeout = SOCKET_TIMEOUT
        self.reconnect_max_attempts = RECONNECT_MAX_ATTEMPTS
        self.log = log
        self.connect()

    def connect(self):
        for i in range(self.reconnect_max_attempts):
            try:
                self.connection = tarantool.Connection(
                    host=self.host,
                    port=self.port,
                    socket_timeout=self.socket_timeout)
            except Exception:
                self.connection = None

    def disconnect(self):
        self.connection = None
        self.port = 100000
        self.connect()

    def get(self, cid):
        try:
            self.conn.ping()
        except Exception:
            self.connect()
        if not self.connection:
            raise tarantool.DatabaseError("Store not connected!")
        tt_int = self.connection.call("get_interests", cid)
        clients_interests = str(tt_int[0])
        clients_interests = clients_interests.replace("\'", "\"")
        return clients_interests

    def cache_get(self, uid):
        try:
            self.conn.ping()
        except Exception:
            self.connect()
        if not self.connection:
            return None
        tt_score = self.connection.call("cache_get_score", uid)
        if tt_score[0]:
            score = "%.1f" % tt_score[0]
        else:
            return None
        return float(score)

    def cache_set(self, *args):
        try:
            self.conn.ping()
        except Exception:
            self.connect()
        if self.connection:
            try:
                fresh_values = (args[0], args[1], args[2])
                self.connection.call("cache_set_score", fresh_values)
                tt_score = self.connection.call("cache_get_score", args[0])
                return tt_score
            except Exception:
                if self.log:
                    logging.warning("Store error!")
                return None
        else:
            if self.log:
                logging.warning("Store not connected!")
            return None

    def cache_delete(self, uid):
        try:
            self.conn.ping()
        except Exception:
            self.connect()
        if self.connection:
            tt = self.connection.space("score")
            tt.delete(uid)
        return self
