#!/usr/bin/env python3

import waitress
import pastebin.app
import sys

default_port = 5260

def usage():
    print(f'usage: {sys.argv[0]} [-h] [-p port]')
    sys.exit(1)

def run(port):
    app = pastebin.app.create_app()
    waitress.serve(app, port=port)

def main():
    if len(sys.argv) == 1:
        port = default_port
    else:
        args = sys.argv[1:]
        for i,arg in enumerate(args):
            if arg == '-h':
                usage()
            if arg == '-p':
                try:
                    port = int(args[i+1])
                except Exception:
                    usage()
    run(port)

if __name__ == "__main__":
    main()

