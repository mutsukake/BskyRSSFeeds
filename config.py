from os import getenv
from dotenv import load_dotenv

# Make sure to call load_dotenv at the beginning to load environment variables
load_dotenv()

def load_config():
    config = {
        "inor_app_id": getenv("inor_app_id"),
        "inor_app_key": getenv("inor_app_key"),
        "inor_access_token": getenv("inor_access_token"),
        "inor_refresh_token": getenv("inor_refresh_token"),
        "bluesky_username": getenv("bluesky_username"),
        "bluesky_password": getenv("bluesky_password"),
        "table_name": getenv("table_name"),
        "inor_redirect_uri": getenv("inor_redirect_uri"),
        "inor_starred_url": getenv("inor_starred_url"),
        "db_name": getenv("db_name"),
    }
    return config
