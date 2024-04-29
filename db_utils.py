from dotenv import load_dotenv
import os
import sqlite3

from inor_utils import get_starred, get_attributes, get_ids

load_dotenv()
DB_NAME = os.getenv("DB_NAME")
TABLE_NAME = os.getenv("TABLE_NAME")

db_path = os.path.join(os.path.dirname(__file__), DB_NAME)

def get_table_data(conn, table_name):
    c = conn.cursor()
    c.execute(f'SELECT * FROM {table_name}')
    return c.fetchall()

def select_starred_items(starred_items, posting_ids):
    
    # Select all the items to be posted by id from starred_items
    selected_items = [item for item in starred_items if item.get('id') in posting_ids]
        
    
    return selected_items
    
def save_items(saving_items, table_name):
    
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

        # Insert each item into the database
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
