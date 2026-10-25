from flask import *

app = Flask(__name__)


@app.route("/update", methods=["POST"])


def init():
    app.run(debug=True, port=3000)

if __name__ == "__main__":
    init()
