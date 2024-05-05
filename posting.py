
from config import load_config
from atproto import Client, client_utils, models
import os
import sqlite3
from typing import Dict
from requests import Session

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
        posting_url = item['url']
        
        session = create_session()

        post = {}  # Define the variable "post"

        post["embed"] = fetch_embed_url_card(session["accessJwt"], posting_url)
        print(post["embed"])
        
        try:
            post = client.send_post(text, embed=post["embed"])
            
        except Exception as e:
            print(e)
            return None
    

def create_session():

    data = {
        "identifier": username,
        "password": password
    }
    headers = {
        "Content-Type": "application/json; charset=UTF-8"
    }
    response = requests.post(create_session_url, data=json.dumps(data), headers=headers)
    print(response)
    accessJwt = response.json()["accessJwt"]
    print(accessJwt) 
    did = response.json()["did"]
    print(did)

    return {
        "accessJwt": accessJwt,
        "did": did
    }