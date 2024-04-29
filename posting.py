
from config import load_config
from atproto import Client, client_utils
import os

# Your credentials

config = load_config()
username = config["bluesky_username"]
password = config["bluesky_password"]

db_path = os.path.join(os.path.dirname(__file__), db_name)

def login_bsky():
    client = Client()
    profile = client.login(username, password)
    print('Welcome,', profile.display_name)
    return client


def posting_bsky(saving_items):
    response = []

    # Connect to the database
    conn = sqlite3.connect(db_path)
    c = conn.cursor()


    client = login_bsky()

    
    for item in saving_items:
        text = f"{item['title']}\n{item['url']}"
    
        post = client.send_post(text)
