"""Simple pastebin module, using sqlite3 for storage."""

from io import BytesIO
import sqlite3
import random
import string
import urllib.parse
import mimetypes
import logging

from constants import MIMETYPE_WHITELIST,TEXT_MIMETYPES

DEFAULT_DB_NAME = 'data.db'

def get_mimetype(filename: str):
    mimetype,_enc = mimetypes.guess_type(filename)
    if mimetype is None:
        return 'application/octet-stream'
    return mimetype

def get_pres_mimetype(mimetype: str):
    """Get the mimetype to send the given mimetype as."""
    if mimetype in TEXT_MIMETYPES or mimetype.startswith('text/'):
        return 'text/plain'
    elif mimetype in MIMETYPE_WHITELIST:
        return mimetype
    return 'application/octet-stream'

def is_url(url: str):
    try:
        parsed = urllib.parse.urlparse(url)
    except ValueError:
        return False
    logging.info(parsed)
    return parsed.scheme == 'http' or parsed.scheme == 'https'

def gen_shortcode(length: int):
    return "".join(random.choice(string.ascii_letters) for c in range(length))

def gen_new_shortcode(conn: sqlite3.Connection, length: int = 3):
    cur = conn.cursor()
    scode = gen_shortcode(length)
    while cur.execute('SELECT shortcode FROM links WHERE shortcode = ?', (scode,)).fetchone():
        scode = gen_shortcode(length)
    return scode

def connect(db_name=DEFAULT_DB_NAME):
    return sqlite3.connect(db_name, isolation_level=None)

def get(conn: sqlite3.Connection, shortcode: str):
    cur = conn.cursor()
    logging.info(f'querying shortcode {shortcode}...')
    link = cur.execute('SELECT * FROM links WHERE shortcode = ?', (shortcode,)).fetchone()
    if link is None:
        return link
    # unpack db row
    _code,link_type,url,mimetype,data = link
    if link_type == 'link':
        return {
            "type": "link",
            "url": url
        }
    elif link_type == 'file':
        return {
            "type": "file",
            "mimetype": mimetype,
            "data": data
        }

def paste_link(conn: sqlite3.Connection, url: str):
    logging.info(f'got link to URL {url}')
    cur = conn.cursor()
    shortcode = gen_new_shortcode(conn)
    logging.info(f'generated link shortcode {shortcode}')
    cur.execute('INSERT INTO links VALUES (?, "link", ?, NULL, NULL)', (shortcode, url))
    return shortcode

def paste_file(conn: sqlite3.Connection, data: bytes, mimetype: BytesIO):
    logging.info(f'received file with mimetype {mimetype}')
    cur = conn.cursor()
    shortcode = gen_new_shortcode(conn)
    logging.info(f'generated file shortcode {shortcode}')
    cur.execute('INSERT INTO links VALUES (?, "file", NULL, ?, ?)', (shortcode, mimetype, data))
    return shortcode

def paste(conn: sqlite3.Connection, type: str, url: str = None, data: bytes = None, mimetype: str = None):
    if type == 'link' and url:
        return paste_link(conn, url)
    elif type == 'file' and data and mimetype:
        return paste_file(conn, data, mimetype)
    return None

def show(db_name=DEFAULT_DB_NAME):
    conn = connect()
    cur = conn.cursor()
    links = cur.execute('SELECT shortcode, type, url, mimetype FROM links').fetchall()
    for link in links:
        print(link)

def reset_db(db_name=DEFAULT_DB_NAME, override=False):
    if not override:
        y = input('Warning: deletes all records from database to reset. Type yes to confirm: ')
        if y.lower() != 'yes':
            print('Aborting.')
            return
    conn = connect(db_name)
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS links')
    cur.execute('CREATE TABLE links (shortcode TEXT NOT NULL, type TEXT NOT NULL, url TEXT, mimetype TEXT, data BLOB)')