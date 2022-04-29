#!/usr/bin/env python3

import waitress
import flask

from app import create_app

if __name__ == "__main__":
    app = create_app()
    waitress.serve(app, port=5260)
