import hashlib
import time

from utils import get_metadata


def get_filename(path, ext):
    with open(path, 'r') as f:
        line = f.readlines()[100]
        md5 = hashlib.md5(line).hexdigest()
        f.seek(0)
        created = get_metadata(f)['created']
        timestamp = int(time.mktime(created.timetuple()))
        filename = '%s-%s' % (timestamp, md5) + '.' + ext
    return filename, created
