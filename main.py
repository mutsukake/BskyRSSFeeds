from inor_utils import *
from db_utils import *
from posting import *
from config import load_config
import yt_utils


def run_inoreader(config):

    inor_refresh_token = config["inor_refresh_token"]
    table_name = config["table_name"]

    # Inoreader authentication and get the access token
    inor_access_token = inor_refresh_access_token(inor_refresh_token)
    if inor_access_token is False:
        return False

    saving_items = get_posting_items(inor_access_token, table_name)

    posted_items = posting_bsky(saving_items)

    # Save only the items that were actually posted to Bluesky
    save_items(posted_items, table_name)


def run_youtube(config):

    # Each source has its own table, so posted ids never mix between sources
    table_name = config["yt_table_name"]

    row_items = yt_utils.get_playlist_items()
    if row_items is None:
        return False

    playlist_items = yt_utils.get_attributes(row_items)
    posted_ids = load_posted_ids(table_name)
    if posted_ids is None:
        return False

    # First run: record what is already in the playlist without posting it
    if len(posted_ids) == 0:
        print(f"First run: marking {len(playlist_items)} existing videos as posted")
        save_items(playlist_items, table_name)
        return

    posted_ids = set(posted_ids)
    new_items = [item for item in playlist_items if item['id'] not in posted_ids]
    if len(new_items) == 0:
        print("No new videos to post")
        return

    posted_items = posting_bsky(new_items)

    # Save only the items that were actually posted to Bluesky
    save_items(posted_items, table_name)


def main():

    config = load_config()

    # A failure in one source must not stop the other
    sources = [("Inoreader", run_inoreader)]
    if config["yt_api_key"] and config["yt_playlist_id"]:
        sources.append(("YouTube", run_youtube))

    for name, run in sources:
        print(f"--- {name} ---")
        try:
            run(config)
        except Exception as e:
            print(f"{name} failed: {e}")


if __name__ == '__main__':
    main()
