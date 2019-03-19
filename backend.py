import socket
import json
from flask import Flask


app = Flask(__name__)

global piggy_global_number
piggy_global_number = 0

@app.route("/")
def hello():
    return "Hello World, from {}".format(socket.gethostname())


@app.route("/backend")
def cat():
    global piggy_global_number
    piggy_global_number += 1

    return json.dumps({
        'status': 200,
        'number': piggy_global_number,
        'hostname': socket.gethostname(),
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
