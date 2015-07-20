from datetime import datetime
import exifread


def get_metadata(f):
    metadata = exifread.process_file(f)
    original_date = metadata['EXIF DateTimeOriginal']
    created = datetime.strptime(original_date.values, '%Y:%m:%d %H:%M:%S')
    return {'created': created}
