import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from werkzeug.serving import WSGIRequestHandler
from flask import Flask, Response, request

from world import *

import argparse
import logging
import json

app = Flask(__name__)

world = World()


def reply(data, code=200):
    return Response(json.dumps(data, separators=(",", ":")), status=code, mimetype="application/json")


def body():
    data = request.get_json(force=True, silent=True)

    return data if isinstance(data, dict) else {}


@app.route("/", methods=["GET"])
@app.route("/status", methods=["GET"])
def status():
    return reply(world.status())


@app.route("/join", methods=["POST"])
def join():
    data = body()

    if data.get("protocol") != PROTOCOL_VERSION:
        return reply({"error": f"protocol mismatch: server uses {PROTOCOL_VERSION}, update the game"}, 400)

    answer = world.join(data.get("name", "Player"))

    if answer is None:
        return reply({"error": "server is full"}, 503)

    return reply(answer)


@app.route("/update", methods=["POST"])
def update():
    code, answer = world.handleUpdate(body())

    return reply(answer, code)


@app.route("/leave", methods=["POST"])
def leave():
    world.leave(str(body().get("id", "")))

    return reply({"ok": True})


def init():
    parser = argparse.ArgumentParser(description="Ascension Protocol server")

    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--difficulty", type=float, default=None)

    args = parser.parse_args()

    world.config = Config(maxPlayers=None, difficulty=args.difficulty)

    logging.getLogger("werkzeug").setLevel(logging.WARNING)

    WSGIRequestHandler.protocol_version = "HTTP/1.1"

    world.start()

    print(f"{NAME} {VERSION} server: http://{args.host}:{args.port} (protocol {PROTOCOL_VERSION})")

    app.run(host=args.host, port=args.port, debug=False, threaded=True, use_reloader=False)


if __name__ == "__main__":
    init()
