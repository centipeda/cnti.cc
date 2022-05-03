#!/usr/bin/env python3

import waitress
import pastebin.app

if __name__ == "__main__":
    app = pastebin.app.create_app()
    waitress.serve(app, port=5260)
