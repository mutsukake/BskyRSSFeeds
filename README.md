# BskyRSSFeeds

Automatically cross-posts your starred [Inoreader](https://www.inoreader.com/) items and new videos from a [YouTube](https://www.youtube.com/) playlist to [Bluesky](https://bsky.app/), complete with a link card (title, description, and thumbnail scraped from the page's OGP tags).

The sources run one after another; each keeps its own table of posted ids, and a failure in one does not stop the other.

## How it works

1. `main.py` refreshes the Inoreader OAuth access token and fetches your starred items (`inor_utils.py`).
2. Items that haven't been posted yet are selected by diffing against a local SQLite database (`db_utils.py`, `posted_ids.db`).
3. Each new item is logged into Bluesky and posted with a link-card embed built from the article's Open Graph metadata (`posting.py`).
4. If `yt_api_key` and `yt_playlist_id` are set, the same is done for the YouTube playlist (`yt_utils.py`), tracked in its own table (`yt_table_name`). The first YouTube run only records the videos already in the playlist and posts nothing; videos added afterwards are posted.
5. Only items that were **successfully** posted are recorded as "posted" in the database, so a failed post (e.g. a site blocking the request) is retried on the next run instead of being silently skipped.

## Requirements

- Python 3.11+
- An Inoreader account with an [OAuth app](https://www.inoreader.com/developers/oauth) (client ID/secret)
- A Bluesky account
- (Optional) A Google Cloud project with the YouTube Data API v3 enabled, for the YouTube source

## Setup

1. Create and activate a virtual environment, then install dependencies:

   ```sh
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy the example environment file and fill in your credentials:

   ```sh
   cp .env.example .env
   ```

   | Variable | Description |
   | --- | --- |
   | `bluesky_username` | Your Bluesky handle (e.g. `example.bsky.social`) |
   | `bluesky_password` | A Bluesky [app password](https://bsky.app/settings/app-passwords) |
   | `inor_app_id` / `inor_app_key` | Your Inoreader OAuth app's client ID/secret |
   | `inor_redirect_url` | OAuth redirect URI registered with your Inoreader app, e.g. `http://localhost:5001/callback` |
   | `inor_oauth_init_server` | The local URL the auth flow opens in your browser, e.g. `http://localhost:5001` |
   | `inor_starred_url` | Inoreader API endpoint for starred items (`https://www.inoreader.com/reader/api/0/stream/contents/user/-/state/com.google/starred`) |
   | `inor_access_token` / `inor_refresh_token` | Filled in automatically by the auth flow below; leave blank initially |
   | `db_name` | SQLite database filename (e.g. `posted_ids.db`) |
   | `table_name` | Table name used to track posted item IDs |

3. Run the one-time OAuth flow to obtain your first access/refresh tokens:

   ```sh
   python inor_init_auth.py
   ```

   This starts a local Flask server, opens your browser to Inoreader's authorization page, and writes the resulting tokens back into `.env` once you approve access.

### YouTube (optional)

Leave `yt_api_key` / `yt_playlist_id` blank to skip YouTube entirely.

1. In the [Google Cloud Console](https://console.cloud.google.com/), enable **YouTube Data API v3** (APIs & Services → Library).
2. Create an API key (APIs & Services → Credentials → Create credentials → API key). Under **API restrictions**, restrict it to YouTube Data API v3 only.
3. Make the playlist **Public** or **Unlisted**. A private playlist can't be read with an API key (it returns `playlistNotFound`).
4. Set the values in `.env`:

   | Variable | Description |
   | --- | --- |
   | `yt_api_key` | The API key from step 2 |
   | `yt_playlist_id` | The `list=` value in the playlist URL (`https://www.youtube.com/playlist?list=PL...`). Not a video id (`v=`). |
   | `yt_table_name` | Table used to track posted video ids (default `posted_youtube`) |

The free quota (10,000 units/day) is far more than this needs: one playlist fetch costs 1 unit per 50 videos.

### Cleaning up when you stop using YouTube

Unused credentials are a risk if they leak, so remove them when you no longer need the YouTube source:

1. Delete the API key: Google Cloud Console → APIs & Services → Credentials → delete the key.
2. Disable the API: APIs & Services → Enabled APIs & services → YouTube Data API v3 → Disable API. (Deleting the key and disabling the API are separate steps; do both.)
3. Clear `yt_api_key` and `yt_playlist_id` in `.env`. The YouTube source is then skipped automatically.

## Running

```sh
./run_script.sh
```

This activates the virtual environment and runs `main.py`, which refreshes the Inoreader token, fetches new starred items and new YouTube playlist videos, and posts them to Bluesky. The refresh token is rotated and saved back to `.env` on every run.

To run on a schedule, add it to your crontab, e.g.:

```
0 7,18 * * * /path/to/BskyRSSFeeds/run_script.sh
```

`clean_log.sh` deletes log files older than 7 days from a `logs/` directory, if you redirect the script's output there.

## Notes

- Bluesky link cards require a reachable `og:image`; images larger than 1MB are resized before upload.
- Some sites block the default `requests` user agent — outbound page requests (for link cards) send a browser-like `User-Agent` to reduce false 403/503 failures.
- If a single item fails to post (network error, blocked request, etc.), it's skipped and retried on the next run rather than stopping the whole batch.
