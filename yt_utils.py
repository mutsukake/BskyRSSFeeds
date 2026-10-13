import requests
from config import load_config

config = load_config()

yt_api_key = config["yt_api_key"]
yt_playlist_id = config["yt_playlist_id"]

PLAYLIST_ITEMS_URL = "https://www.googleapis.com/youtube/v3/playlistItems"
WATCH_URL = "https://www.youtube.com/watch?v="

# Titles YouTube returns for videos we cannot (or should not) post
UNAVAILABLE_TITLES = {"Private video", "Deleted video"}


def get_playlist_items():
    """Fetches every video in the public YouTube playlist, following pagination."""
    items = []
    params = {
        "part": "snippet",
        "playlistId": yt_playlist_id,
        "maxResults": 50,
        "key": yt_api_key,
    }

    while True:
        response = requests.get(PLAYLIST_ITEMS_URL, params=params, timeout=10)
        if response.status_code != 200:
            print('Failed to fetch data from YouTube:', response.status_code, response.text)
            return None

        data = response.json()
        items.extend(data.get('items', []))

        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            return items
        params['pageToken'] = next_page_token


def get_attributes(row_items):
    """Converts playlist items into the {'id', 'title', 'url'} shape used by the DB and posting code."""
    result = []
    for item in row_items:
        snippet = item.get('snippet', {})
        title = snippet.get('title')
        video_id = snippet.get('resourceId', {}).get('videoId')
        if not video_id or title in UNAVAILABLE_TITLES:
            continue
        result.append({'id': video_id, 'title': title, 'url': WATCH_URL + video_id})

    return result
