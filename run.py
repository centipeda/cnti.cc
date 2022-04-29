#!/usr/bin/env python3

import waitress
import flask

app = flask.Flask(__name__)

if __name__ == "__main__":
    waitress.serve(app, port=5260)
