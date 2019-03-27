import socket
import json
import MySQLdb
import os
from contextlib import closing
from flask import Flask, g


class NumberStorage:
    def _env(self, key):
        """ Requires MYSQL_* env value """
        value = os.getenv('MYSQL_' + key)
        if value is None:
            raise ValueError('Missing env MYSQL_' + key)
        return value

    def __init__(self):
        self.db = MySQLdb.connect(
            host=self._env('HOST'),
            user=self._env('USER'),
            passwd=self._env('PASSWORD'),
            db=self._env('DATABASE'),
            use_unicode=True)
        self._initialize_db()

    def __del__(self):
        self.close()

    def close(self):
        if self.db:
            self.db.close()
        self.db = None

    def _initialize_db(self):
        with closing(self.db.cursor()) as c:
            c.execute("CREATE TABLE IF NOT EXISTS numbers (name VARCHAR(10) PRIMARY KEY, value INT UNSIGNED)")
            c.execute("INSERT IGNORE INTO numbers (name, value) VALUES ('the_number', 0)")

    def increment_and_get_number(self):
        with closing(self.db.cursor()) as c:
            try:
                c.execute('START TRANSACTION')
                c.execute("UPDATE numbers SET value = value + 1 WHERE name = 'the_number'")
                c.execute("SELECT value FROM numbers WHERE name = 'the_number'")
                new_value = c.fetchone()[0]
                c.execute('COMMIT')
                return new_value
            except Exception:
                c.execute('ROLLBACK')
                raise


app = Flask(__name__)


def get_store():
    if 'store' not in g:
        g.store = NumberStorage()
    return g.store


@app.teardown_appcontext
def teardown_store(exc):
    store = g.pop('store', None)
    if store is not None:
        store.close()


@app.route("/")
def hello():
    return "Hello World, from {}".format(socket.gethostname())


@app.route("/backend")
def cat():
    number = get_store().increment_and_get_number()

    return json.dumps({
        'status': 200,
        'number': number,
        'hostname': socket.gethostname(),
    })

@app.route("/ready")
def ready():
    # check we have store
    get_store()
    return 'OK'


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
