#!/usr/bin/env python

import os
import sys
import shutil
import filecmp
import hashlib
from datetime import datetime
import time

import exifread


def get_metadata(f):
    metadata = exifread.process_file(f)
    original_date = metadata['EXIF DateTimeOriginal']
    created = datetime.strptime(original_date.values, '%Y:%m:%d %H:%M:%S')
    return {'created': created}


def get_filename(path):
    with open(path, 'r') as f:
        line = f.readlines()[100]
        md5 = hashlib.md5(line).hexdigest()
        f.seek(0)
        created = get_metadata(f)['created']
        timestamp = int(time.mktime(created.timetuple()))
        filename = '%s-%s' % (timestamp, md5) + '.NEF'
    return filename, created


def get_outpath(path, to):
    filename, created = get_filename(path)
    directory = os.path.join(
        to, str(created.year), str(created.month), str(created.day))
    return os.path.join(directory, filename)


def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def copy(path, outpath, compare=False):
    error = None
    if os.path.exists(outpath):
        state = 'already exists in'
        if compare and not filecmp.cmp(path, outpath, shallow=True):
            error = {'filename': path, 'outpath': outpath}
    else:
        shutil.copy2(path, outpath)
        state = 'copied to'
    return {'state': state, 'error': error}


def total(path):
    counter = 0
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename.endswith('.NEF'):
                counter += 1
    return counter


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print """
        This small application help organizing raw Nikon images in an external
        drive. Use it with caution.

        --compare: compares existing files with current ones and returns an
        error log at the end if they don't match.

        example usage:
        python rawganize.py <path> <external-drive-path> --compare"""
        sys.exit(1)

    cwd = sys.argv[1]
    to = sys.argv[2]
    compare = False
    if len(sys.argv) > 3 and sys.argv[3] == '--compare':
        compare = True
    errors = []

    total_photos = total(cwd)
    counter = 0
    for root, dirs, files in os.walk(cwd):
        for filename in files:
            if filename.endswith('.NEF'):
                path = os.path.join(root, filename)
                outpath = get_outpath(path, to)
                create_directory(os.path.dirname(outpath))
                result = copy(path, outpath, compare)
                counter += 1
                if result.get('error'):
                    errors.append(result.get('error'))
                print('%s/%s - %s %s %s' % (
                    counter, total_photos, path, result.get('state'),
                    outpath.replace(to, '')))

    if errors:
        print("ERRORS:")
        print(errors)
