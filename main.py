from inor_utils import *
from db_utils import *
from posting import *
from config import load_config



def main():

    config = load_config()
    
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
    
if __name__ == '__main__':
    main()