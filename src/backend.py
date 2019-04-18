import socket
import json
from flask import Flask, g
from storage import NumberStorage


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


@app.route("/reset-info")
def reset_info():
    info = get_store().reset_info()
    return json.dumps({
        'status': 200,
        'count': info['count'],
        'last': info['last'].strftime('%Y-%m-%d %H:%M:%S'),
    })


@app.route("/ready")
def ready():
    # check we have store
    get_store()
    return 'OK'


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
