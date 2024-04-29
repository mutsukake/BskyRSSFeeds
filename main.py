from inor_utils import *
from twitter_utils import *
from db_utils import *

from config import load_configuration

def main():

    config = load_configuration()
    
    inor_refresh_token = config["inor_refresh_token"]
    table_name = config["table_name"]

    # Inoreader authentication and get the access token
    inor_access_token = inor_refresh_access_token(inor_refresh_token)
    if inor_access_token is False:
        return False

    # Save the new starred items to the database
    row_starred_items = get_starred(inor_access_token)
    starred_item = get_attributes(row_starred_items)
    starred_ids = get_ids(starred_item)

    # Get the posted ids from the database
    posted_ids = load_posted_ids(table_name)

    print(f"posted_ids: {posted_ids}")
    print(f"starred_ids: {starred_ids}")

    posting_ids = set(starred_ids) - set(posted_ids)
    if len(posting_ids) == 0:
        print("No new items to post")
        return
    print(f"posting_ids: {posting_ids}")

    # Retrieve the items to be saved from ids
    saving_items = select_starred_items(starred_item, posting_ids)

    save_items(saving_items, table_name)
    
    posting_bsky(saving_items)
    
if __name__ == '__main__':
    main()