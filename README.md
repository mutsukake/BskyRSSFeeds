# TweetRSSfeeds

Prerequisites:
- Inoreader account
- Twitter account
- Python 3.9.6


# Setup
1. Clone the repository
```
git clone
```
2. Create a virtual environment
```
source venv/bin/activate
```

## Installation

3. Create a file called `.env` in the root directory of the project. Add the following lines to the file:

1.  Initial authentication is required to access the Inoreader API. To do this, run the following command in the terminal:

```
python inoreader_init_auth.py
```

- This will open a browser window and prompt you to log in to your Inoreader account. Once you have logged in, you will be redirected to a page with a code. 

2. Initial authentication for Twitter is also required. To do this, run the following command in the terminal:

```
python twitter_init_auth.py
```

- This will open a browser window and prompt you to log in to your Twitter account. Once you have logged in, you will be redirected to a page with a code.


```