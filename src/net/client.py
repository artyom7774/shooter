from src.net.protocol import *

import http.client
import threading
import json
import time


class NetClient:
    def __init__(self, game, host="127.0.0.1", port=DEFAULT_PORT, name="Player"):
        self.game = game

        self.host = host
        self.port = port
        self.name = name

        self.enabled = False

        self.status = "off"
        self.error = ""

        self.id = None
        self.color = 0
        self.ping = 0

        self.lock = threading.Lock()

        self.thread = None
        self.running = False
        self.session = 0

        self.state = {}
        self.outbox = []
        self.eventNumber = 0

        self.inbox = []
        self.serverAck = 0
        self.ackToServer = 0

        self.joinInfo = None

        self.connection = None

    @property
    def address(self):
        return f"{self.host}:{self.port}"

    def join(self):
        self.leave()

        with self.lock:
            self.session += 1

            self.status = "connecting"
            self.error = ""

            self.id = None
            self.joinInfo = None

            self.outbox = []
            self.inbox = []
            self.eventNumber = 0
            self.serverAck = 0
            self.ackToServer = 0

            self.running = True

        self.thread = threading.Thread(target=self.run, args=(self.session,), name="net", daemon=True)
        self.thread.start()

    def leave(self, wait=False):
        with self.lock:
            was = self.running and self.id is not None
            pid = self.id

            self.running = False
            self.session += 1

            self.status = "off"

            self.id = None

        if not was:
            return

        def goodbye():
            try:
                connection = http.client.HTTPConnection(self.host, self.port, timeout=1.5)
                connection.request("POST", "/leave", json.dumps({"id": pid}), {"Content-Type": "application/json"})
                connection.getresponse().read()
                connection.close()

            except Exception:
                pass

        thread = threading.Thread(target=goodbye, name="net-leave", daemon=True)
        thread.start()

        if wait:
            thread.join(2)

    def setState(self, state):
        self.state = state

    def send(self, event):
        with self.lock:
            self.eventNumber += 1

            self.outbox.append([self.eventNumber, *event])

            if len(self.outbox) > 500:
                del self.outbox[:len(self.outbox) - 500]

    def takeResponses(self):
        with self.lock:
            answers = self.inbox

            self.inbox = []

        return answers

    def onLocalBullet(self, bullet):
        if self.status != "online" or not self.game.online:
            return

        if bullet.another.get("type") == "explosive":
            return

        self.send(["s", round(bullet.x, 1), round(bullet.y, 1), round(bullet.angle, 1), bullet.speed, bullet.radius, bullet.liveTime])

    def sendDamage(self, enemyId, damage):
        if self.status == "online":
            self.send(["d", enemyId, round(damage, 3)])

    def request(self, path, data, timeout=3.0):
        payload = json.dumps(data, separators=(",", ":"))

        for attempt in range(2):
            if self.connection is None:
                self.connection = http.client.HTTPConnection(self.host, self.port, timeout=timeout)

            try:
                self.connection.request("POST", path, payload, {"Content-Type": "application/json"})

                response = self.connection.getresponse()

                raw = response.read()

                return response.status, json.loads(raw.decode("utf-8") or "{}")

            except (http.client.HTTPException, OSError, ValueError):
                try:
                    self.connection.close()

                except Exception:
                    pass

                self.connection = None

                if attempt == 1:
                    raise

        raise ConnectionError("unreachable")

    def alive(self, session):
        return self.running and self.session == session

    def run(self, session):
        self.connection = None

        period = 1 / SEND_RATE

        while self.alive(session):
            started = time.perf_counter()

            try:
                if self.id is None:
                    self.handshake(session)

                else:
                    self.exchange(session)

                    self.ping = round((time.perf_counter() - started) * 1000)

            except Exception as error:
                if not self.alive(session):
                    break

                self.fail(session, f"{type(error).__name__}: {error}" if str(error) else type(error).__name__)

                time.sleep(1.5)

                continue

            if self.id is not None:
                time.sleep(max(0, period - (time.perf_counter() - started)))

            else:
                time.sleep(0.05)

        try:
            if self.connection is not None:
                self.connection.close()

        except Exception:
            pass

        self.connection = None

    def fail(self, session, text):
        with self.lock:
            if self.session != session:
                return

            self.status = "error" if self.id is None else "connecting"
            self.error = text

            self.id = None

    def handshake(self, session):
        code, answer = self.request("/join", {"name": self.name, "protocol": PROTOCOL_VERSION})

        if code != 200:
            raise ConnectionError(answer.get("error", f"HTTP {code}"))

        with self.lock:
            if self.session != session:
                return

            self.id = answer["id"]
            self.color = answer.get("color", 0)
            self.joinInfo = answer

            self.status = "online"
            self.error = ""

            self.outbox = []
            self.eventNumber = 0
            self.serverAck = 0
            self.ackToServer = 0

    def exchange(self, session):
        with self.lock:
            outbox = list(self.outbox)

            ack = self.ackToServer

        code, answer = self.request("/update", {"id": self.id, "st": self.state, "ev": outbox, "ack": ack})

        if code == 404:
            raise ConnectionError("session lost")

        if code != 200:
            raise ConnectionError(answer.get("error", f"HTTP {code}"))

        with self.lock:
            if self.session != session:
                return

            self.serverAck = max(self.serverAck, answer.get("ack", 0))

            self.outbox = [event for event in self.outbox if event[0] > self.serverAck]

            self.inbox.append(answer)

            if len(self.inbox) > 60:
                del self.inbox[:len(self.inbox) - 60]

    def confirm(self, number):
        self.ackToServer = max(self.ackToServer, number)
