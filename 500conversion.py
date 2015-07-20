import requests
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("username")
parser.add_argument("--sortby", default='votes_rate')
args = parser.parse_args()

username = args.username
sort_by = args.sortby

base_url = 'https://api.500px.com/v1/'
consumer_key = 'VlcvNFqOSJhNJMZJ0Lu79asODCce9QEUayOUHqAL'

url = lambda endpoint: base_url + endpoint

ALL_PHOTOS = []


def calculate_conversions(photo):
    views = photo['times_viewed']
    votes = photo['votes_count']
    favs = photo['favorites_count']

    if views > 0:
        votes_rate = 100.0 * votes / views
        favs_rate = 100.0 * favs / views
    else:
        votes_rate = 0.0
        favs_rate = 0.0

    return {
        'name': photo['name'],
        'views': views,
        'votes': votes,
        'favs': favs,
        'votes_rate': votes_rate,
        'favs_rate': favs_rate}


def get_photos(page=1):
    r = requests.get(
        url('photos'),
        data={'feature': 'user',
              'username': username,
              'page': page,
              'consumer_key': consumer_key})

    if r.ok:
        results = r.json()
        for photo in results['photos']:
            ALL_PHOTOS.append(calculate_conversions(photo))

        if page < results['total_pages']:
            get_photos(page + 1)

get_photos()


ALL_PHOTOS = sorted(ALL_PHOTOS, key=lambda x: x[sort_by], reverse=True)

for photo in ALL_PHOTOS:
    print("""
%s
views: %s
votes: %s
favs: %s
votes rate: %.2f%%
favs rate: %.2f%%
""" % (photo['name'], photo['views'], photo['votes'],
       photo['favs'], photo['votes_rate'], photo['favs_rate']))
