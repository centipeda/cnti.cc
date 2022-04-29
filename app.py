
# standard library
import io
import mimetypes
import logging

# extra libraries
from flask import Flask, redirect, request, g, abort, send_file
from werkzeug.utils import secure_filename

# our libraries
import pastebin

DB_NAME = 'data.db'
LOGFILE_NAME = 'pastebin.log'
pastebin.DEFAULT_DB_NAME = DB_NAME
logging.basicConfig(filename=LOGFILE_NAME, level=logging.INFO)

def create_app():
    app = Flask(__name__)
    app.config['DB_FILE'] = DB_NAME
    app.config['MAX_CONTENT_LENGTH'] = 1000*1000*1000

    def get_connection():
        return g.get('links')

    @app.before_request
    def set_connection():
        if 'links' not in g:
            g.links = pastebin.connect(app.config['DB_FILE'])

    @app.route("/paste", methods=["GET"])
    @app.route("/", methods=["GET"])
    def index():
        return "Welcome to the pastebin."

    @app.route("/paste", methods=["POST"])
    def paste():
        try:
            files = request.files.values()
            file = next(files)
        except StopIteration:
            abort(400, 'no file uploaded')
        if len(request.files) > 1:
            abort(400, description='too many files')
        filename = secure_filename(file.filename)
        mimetype = pastebin.get_mimetype(filename)
        with io.BytesIO() as buf:
            data = b''
            file.save(buf)
            buf.seek(0)
            data = buf.read()
        conn = get_connection()
        shortcode = pastebin.paste(conn, type='file', mimetype=mimetype, data=data)
        if shortcode:
            return f"{request.host}/{shortcode}"
        abort(500, description="Failed to create pastelink.")
    
    @app.route("/short", methods=["POST"])
    def short():
        raw_data = request.get_data()
        body_data = raw_data.decode('utf8')
        if pastebin.is_url(body_data):
            conn = get_connection()
            shortcode = pastebin.paste(conn, 'link', url=body_data)
            if shortcode:
                return f"{request.host}/{shortcode}"
            abort(500, description="Failed to create shortlink.")

    # don't name this redirect
    @app.route("/<string:link_id>", methods=["GET"])
    def link(link_id):
        conn = get_connection()
        link = pastebin.get(conn, link_id)
        if link:
            if link['type'] == 'link':
                logging.info(f'redirecting to {link["url"]}')
                return redirect(link['url'])
            elif link['type'] == 'file':
                # figure out mimetype and extension
                ext = mimetypes.guess_extension(link['mimetype'])
                if ext is None:
                    ext = ""
                shown_mtype = pastebin.get_pres_mimetype(link['mimetype'])

                # construct mimetype from extension
                fname = f"{link_id}{ext}"
                # open data as file-like bytes
                file = io.BytesIO(link['data'])

                # only text/image/video/audio should be sent as itself
                # everything else should be downloaded
                as_attachment = True
                if shown_mtype.startswith("text/") or \
                   shown_mtype.startswith("image/") or \
                   shown_mtype.startswith("video/") or \
                   shown_mtype.startswith("audio/"):
                    as_attachment = False
                logging.info(f'sending {fname}')
                return send_file(
                    path_or_file=file,
                    mimetype=shown_mtype,
                    as_attachment=as_attachment,
                    download_name=fname,
                    attachment_filename=fname
                )
        return abort(404)

    return app

create_app()
