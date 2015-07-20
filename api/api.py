import os
from flask import Flask, request, jsonify
from werkzeug import secure_filename

UPLOAD_FOLDER = '/Users/macellan/Desktop/output/'
ALLOWED_EXTENSIONS = set(['NEF', 'SRW'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def is_allowed(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return jsonify(**{'results': os.listdir(UPLOAD_FOLDER)})

    elif request.method == 'POST':
        image = request.files.get('image')
        if image and is_allowed(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(UPLOAD_FOLDER, filename))


if __name__ == "__main__":
    app.run(debug=True)
