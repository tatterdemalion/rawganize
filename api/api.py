import os
import hashlib
import time

from datetime import datetime
import exifread
from rawkit.raw import Raw

from flask import Flask, request, jsonify
from werkzeug import secure_filename

ALLOWED_EXTENSIONS = set(['NEF', 'SRW'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/Users/macellan/Desktop/output/'
app.config['MEDIA_HOST'] = 'http://localhost:5001/'


def get_metadata(stream):
    metadata = exifread.process_file(stream)
    original_date = metadata['EXIF DateTimeOriginal']
    created = datetime.strptime(original_date.values, '%Y:%m:%d %H:%M:%S')
    stream.seek(0)  # make the stream reusable
    return {'created': created}


def get_filename(filename, created):
    md5 = hashlib.md5(filename).hexdigest()
    timestamp = int(time.mktime(created.timetuple()))
    ext = os.path.splitext(filename)[1]
    filename = '%s-%s' % (timestamp, md5) + ext
    return filename


def get_outpath(filename, created_path):
    directory = os.path.join(
        app.config['UPLOAD_FOLDER'], created_path)
    path = os.path.join(directory, filename)
    return path


def get_path_by_created(created):
    return os.path.join(str(created.year), str(created.month),
                        str(created.day))


def check_outpath(path):
    return not os.path.exists(path)


def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def is_allowed(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route("/", methods=['GET', 'PUT'])
def index():
    upload_to = app.config['UPLOAD_FOLDER']
    if request.method == 'GET':
        path = request.args.get('path')
        base_url = app.config['MEDIA_HOST']
        if path:
            base_url = base_url + path + '/'
            path = os.path.join(upload_to, path)
        else:
            path = upload_to
        files = map(lambda x: base_url + x, os.listdir(path))
        return jsonify(**{'results': files})

    elif request.method == 'PUT':
        image = request.files.get('image')
        if image and is_allowed(image.filename):
            metadata = get_metadata(image.stream)
            created = metadata['created']
            created_path = get_path_by_created(created)
            filename = get_filename(secure_filename(image.filename),
                                    created)
            base_filename = os.path.splitext(filename)[0]
            outpath = get_outpath(filename, created_path)
            if 1:  # check_outpath(outpath):
                create_directory(os.path.dirname(outpath))
                image.save(outpath)
                export_path = os.path.join(
                    upload_to, 'exports', created_path, base_filename + '.jpg')
                raw = Raw(filename=outpath)
                create_directory(os.path.dirname(export_path))
                raw.save_thumb(export_path)
                return jsonify(**{'results': True})
        return jsonify(**{'results': False})


if __name__ == "__main__":
    app.run(debug=True)
