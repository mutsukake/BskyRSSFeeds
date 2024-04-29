import requests
from dotenv import load_dotenv
import os
import json
import sqlite3
from config import load_config

config = load_config()

inor_app_id = config["inor_app_id"]
inor_app_key = config["inor_app_key"]
inor_access_token = config["inor_access_token"]
inor_refresh_access_token = config["inor_refresh_token"]
table_name = config["table_name"]
db_name = config["db_name"]
inor_redirect_url = config["inor_redirect_uri"]
inor_starred_url = config["inor_starred_url"]

db_path = os.path.join(os.path.dirname(__file__), db_name)

ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')

# Inoreader GET URL for starred items

def inor_refresh_access_token(refresh_token):
    token_url = 'https://www.inoreader.com/oauth2/token'
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': inor_app_id,
        'client_secret': inor_app_key
    }
    session = requests.Session()
    response = requests.post(token_url, data=data)
    
    if response.status_code == 200:
        print('Successfully refreshed token')
        response_data = response.json()
        
        access_token = response.json().get('access_token')
        new_refresh_token = response.json().get('refresh_token')

        with open(ENV_PATH, 'r') as file:
                lines = file.readlines()
            # Overwrite the variables
        for i, line in enumerate(lines):
            if line.startswith('inor_access_token'):
                lines[i] = f"inor_access_token={access_token}\n"
            elif line.startswith('inor_refresh_token'):
                lines[i] = f"inor_refresh_token={new_refresh_token}\n"

        # Write the file back out
        with open(ENV_PATH, 'w') as file:
            file.writelines(lines)
        
        return access_token
        
    else:
        print('Failed to refresh token:', response.status_code)
        return False


def get_starred(access_token):
    
    """Fetches starred items from inor."""
    session = requests.Session()
    session.headers.update({'Authorization': f'Bearer {access_token}'})
     # Now you can use session to make requests, and the header will be included
    response = session.get(inor_starred_url)

    # Example API call
    if response.status_code == 200:
        print(f"Status code: {response.status_code}")
        # Process the data
        data = response.json()
        return data.get('items', [])
    else:
        return 'Failed to fetch data from Inoreader.', response.status_code

def get_attributes(row_starred_items):
    
    result = []
    for item in row_starred_items:
        id = item.get('id')
        title = item.get('title')
        url = item.get('canonical')[0].get('href') if item.get('canonical') else None
        result.append({'id': id, 'title': title, 'url': url})
        
    return result    

def save_starred_inor():
    """Saves starred items to a database."""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
    # Save all contents of the starred items
        for item in get_starred():
            insert_items_sql = '''INSERT OR IGNORE INTO posted_ids VALUES (?)'''
            c.execute(insert_items_sql, (json.dumps(item),))
            print(f"Added {item['id']} to the database")

    except sqlite3.Error as e:
        print(f"An error occurred: {str(e)}")

    finally:
        print("Committing changes to the database")
        conn.commit()
    
def some_protected_page(access_token):
    session = requests.Session()

    # Set the Authorization and AppId headers
    session.headers.update({
        'Authorization': f'Bearer {access_token}',
        'AppId': inor_app_id  # Replace with your actual AppId
    })

    # Make a request using the session
    response = session.get('https://www.inoreader.com/reader/api/0/user-info')
    
    print(f"Status code: {response.status_code}")
    print(f"Response body: {response.text}")

    if response.status_code == 200:
        # Process the data
        data = response.json()
        print(f"succesfully fetched data: {response.status_code}")
    else:
        # Debug: Print response details for error analysis
        print(response.json())
        return "Failed to fetch data from Inoreader.", response.status_code

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

def get_posting_ids(posted_ids, starred_ids):

    posting_ids = set(starred_ids) - set(posted_ids)

    # Print what's going to be posted
    print(f"Going to post the item's ids: {posting_ids}")
    
    return posting_ids

def get_ids(items):
    """Returns a list of starred item IDs."""
    fetched_ids = [item.get('id') for item in items]
    
    return fetched_ids
