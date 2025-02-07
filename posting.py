
from config import load_config
from atproto import Client
import os
import sqlite3
from typing import Dict
from bs4 import BeautifulSoup
import requests
from requests import Session
from PIL import Image
from io import BytesIO

import json


# Your credentials

config = load_config()
username = config["bluesky_username"]
password = config["bluesky_password"]
db_name = config["db_name"]
db_path = os.path.join(os.path.dirname(__file__), db_name)

create_session_url = "https://bsky.social/xrpc/com.atproto.server.createSession" 

def login_bsky():
    client = Client()
    profile = client.login(username, password)
    print('Welcome,', profile.display_name)
    return client


def get_ogp_image_url(url):
    response = requests.get(url)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, 'html.parser')
    og_image = soup.find('meta', property='og:image')
    if og_image:
        return og_image['content']
    else:
        return None

def fetch_embed_url_card(access_token: str, url: str) -> Dict:

    IMAGE_MIMETYPE = "image/jpeg"

    # the required fields for every embed card
    card = {
        "uri": url,
        "title": "",
        "description": "",
    }

    # fetch the HTML
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # parse out the "og:title" and "og:description" HTML meta tags
    title_tag = soup.find("meta", property="og:title")
    if title_tag:
        card["title"] = title_tag["content"]
    description_tag = soup.find("meta", property="og:description")
    if description_tag:
        card["description"] = description_tag["content"]

    # if there is an "og:image" HTML meta tag, fetch and upload that image
    image_tag = soup.find("meta", property="og:image")
    if image_tag:
        img_url = image_tag["content"]
        # naively turn a "relative" URL (just a path) into a full URL, if needed
        if "://" not in img_url:
            img_url = url + img_url
        resp = requests.get(img_url)
        
        resp.raise_for_status()

        TEMP_IMAGE_PATH = "temp.jpg"
        # if the image is too large, resize it
        if len(resp.content) > 1024 * 1024:
                img = Image.open(BytesIO(resp.content))
                img.save(TEMP_IMAGE_PATH, optimize=True, quality=85)
                while os.path.getsize(TEMP_IMAGE_PATH) > 1024 * 1024:
                    img = img.resize(
                        (img.size[0] // 2, img.size[1] // 2), Image.ANTIALIAS
                    )
                    img.save(TEMP_IMAGE_PATH, optimize=True, quality=85)
                with open(TEMP_IMAGE_PATH, "rb") as f:
                    resp.content = f.read()

        blob_resp = requests.post(
            "https://bsky.social/xrpc/com.atproto.repo.uploadBlob",
            headers={
                "Content-Type": IMAGE_MIMETYPE,
                "Authorization": "Bearer " + access_token,
            },
            data=resp.content,
        )
        blob_resp.raise_for_status()
        card["thumb"] = blob_resp.json()["blob"]

    return {
        "$type": "app.bsky.embed.external",
        "external": card,
    }

def posting_bsky(saving_items):

    # Connect to the database
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    client = login_bsky()

    # Exception handling when the data is not found
    if saving_items is None:
            return None

    for item in saving_items:
        text = item['title']
        # trim_text_to_limit(text)
        
        posting_url = item['url']
        
        session = create_session()

        post = {}  # Define the variable "post"

        post["embed"] = fetch_embed_url_card(session["accessJwt"], posting_url)
        print(post["embed"])
        
        try:
            post = client.send_post(text, embed=post["embed"])
            
        except Exception as e:
            print(e)
            continue # Continue with the next item
    

def create_session():

    data = {
        "identifier": username,
        "password": password
    }
    headers = {
        "Content-Type": "application/json; charset=UTF-8"
    }
    try:
        response = requests.post(create_session_url, data=json.dumps(data), headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        if response.status_code == 406:
            return
    
    print(response)

    accessJwt = response.json()["accessJwt"]
    did = response.json()["did"]
    
    return {
        "accessJwt": accessJwt,
        "did": did
    }

def trim_text_to_limit(text, limit=300):
    if len(text) > limit:
        return text[:limit]
    return text
