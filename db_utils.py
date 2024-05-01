from dotenv import load_dotenv
import os
import sqlite3
from config import load_config

from inor_utils import get_starred, get_attributes, get_ids
config = load_config()
table_name = config["table_name"]
db_name = config["db_name"]

db_path = os.path.join(os.path.dirname(__file__), db_name)


def select_starred_items(starred_items, posting_ids):
    
    # Select all the items to be posted by id from starred_items
    selected_items = [item for item in starred_items if item.get('id') in posting_ids]
        
    
    return selected_items
    
def save_items(saving_items, table_name):
    
    if saving_items is None:
        return None

    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        # Create the table if it doesn't exist
        c.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id TEXT PRIMARY KEY,
                title TEXT,
                url TEXT
            )
        ''')
        

        for item in saving_items:
                c.execute(f'''
                        INSERT OR REPLACE INTO {table_name} VALUES (?, ?, ?)
                    ''', (item.get('id'), item.get('title'), item.get('url')))

        conn.commit()
        
        # Select and print the items
        c.execute(f'SELECT * FROM {table_name}')
        saved_items = c.fetchall()
        print(f"items saved: {saved_items}")
        return saved_items
        
    except sqlite3.Error as e:
        print(f"An error occurred: {str(e)}")

    finally:
        if conn:
            conn.close()

def load_posted_ids(table_name):
    """Loads the IDs of posted items from the database."""
    posted_ids = []
    
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
                    # Create the table if it doesn't exist
            c.execute(f'''
                CREATE TABLE IF NOT EXISTS {table_name} (
                id TEXT PRIMARY KEY,
                title TEXT,
                url TEXT
            )
            ''')
            
            c.execute(f'SELECT id FROM {table_name}')
            
            posted_ids = [row[0] for row in c.fetchall()]
    except sqlite3.Error as e:
        print(f"An error occurred: {str(e)}")
        return None

    finally:
        if conn:
            conn.close()
    return posted_ids

def get_posting_items(inor_access_token, table_name):

    # Save the new starred items to the database
    row_starred_items = get_starred(inor_access_token)
    starred_item = get_attributes(row_starred_items)
    starred_ids = get_ids(starred_item)

    # Get the posted ids from the database
    posted_ids = load_posted_ids(table_name)

    # print(f"posted_ids: {posted_ids}")
    # print(f"starred_ids: {starred_ids}")

    posting_ids = set(starred_ids) - set(posted_ids)
    if len(posting_ids) == 0:
        print("No new items to post")
        # end the function
        return None
    else:
        print(f"posting_ids: {posting_ids}")
        result = select_starred_items(starred_item, posting_ids)
        return result
