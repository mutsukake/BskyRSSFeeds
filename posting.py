
from config import load_config
from atproto import Client, client_utils, models
import os
import sqlite3
import httpx
import asyncio

# Your credentials

config = load_config()
username = config["bluesky_username"]
password = config["bluesky_password"]

db_name = config["db_name"]

db_path = os.path.join(os.path.dirname(__file__), db_name)

def login_bsky():
    client = Client()
    profile = client.login(username, password)
    print('Welcome,', profile.display_name)
    return client

from bs4 import BeautifulSoup
import requests

def get_ogp_image_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    og_image = soup.find('meta', property='og:image')
    if og_image:
        return og_image['content']
    else:
        return None

async def fetch_and_upload_image(ogp_img_url, agent, url, title, ogp_text):
    
    image_data = ogp_img_url

    # Upload the image
    upload_response = await agent.upload_blob(bytearray(image_data), {
        'encoding': 'image/jpeg',
    })
    upload_data = upload_response.json()

    # Prepare the embed parameters
    embed_params = {
        '$type': 'app.bsky.embed.external',
        'external': {
            'uri': url,
            'thumb': {
                '$type': 'blob',
                'ref': {
                    '$link': str(upload_data['blob']['ref']),
                },
                'mimeType': upload_data['blob']['mimeType'],
                'size': upload_data['blob']['size'],
            },
            'title': title,
            'description': ogp_text,
        },
    }
    return embed_params

# Example usage (you need to define `agent`, `ogp_img_url`, `tenki_url`, `title`, `ogp_text`)
# asyncio.run(fetch_and_upload_image(ogp_img_url, agent, tenki_url, title, ogp_text))


def posting_bsky(saving_items):

    # Connect to the database
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    client = login_bsky()

    # Exception handling when the data is not found
    if saving_items is None:
            return None

    for item in saving_items:

        title = item['title']  # Direct use of 'title'
        url = item['url']
        # Ensure 'TextBuilder' constructs the text and link correctly
        text = client_utils.TextBuilder().text(title)

        # Get the OGP image URL
        ogp_img_url = get_ogp_image_url(url)
        
        # Get the image name
        ogp_img_name = ogp_img_url.split('/')[-1]

        # Prepare the embed parameters
        thumb = client.upload_blob(ogp_img_name, bytearray(ogp_img_url), {
            'encoding': 'image/jpeg',
        })
        
        print(thumb.blob)

        embed = models.AppBskyEmbedExternal.Main(
            external=models.AppBskyEmbedExternal.External(
                uri=url,
                thumb=thumb.blob.ref.IpldLink.link,
                title=title,
                description=title,
                

            )
        )
        print(embed)
        
        
        # try:
        #     post = client.send_post(text, embed=embed)
        #     return post
        # except Exception as e:
        #     print(f"Failed to send post for {title}: {e}")


