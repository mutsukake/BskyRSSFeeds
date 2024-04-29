from flask import Flask, request, redirect, session
import requests
import webbrowser
import secrets
import os
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a secure secret key

# Replace these with your Inoreader client ID and secret
load_dotenv()
inor_APP_ID = os.getenv("inor_APP_ID")
inor_APP_KEY = os.getenv("inor_APP_KEY")
inor_REDIRECT_URI = os.getenv("inor_REDIRECT_URI")
inor_OAUTH_INIT_SERVER = os.getenv("inor_OAUTH_INIT_SERVER")
ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')

port = 5001


@app.route('/')
def home():

    # Generate a random string for CSRF protection
    state = secrets.token_hex(16)
    session['oauth_state'] = state

    # Redirect to Inoreader's authorization URL
    auth_url = f"https://www.inoreader.com/oauth2/auth?client_id={inor_APP_ID}&redirect_uri=http://localhost:5001/callback&response_type=code&scope=read write&state={state}"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    state = request.args.get('state')
    if state != session.get('oauth_state'):
        return "State mismatch. Potential CSRF attack.", 400

    # Extract the 'code' from the callback URL
    code = request.args.get('code')

    if code:
        # Exchange the code for an access token
        token_url = 'https://www.inoreader.com/oauth2/token'
        data = {
            'client_id': inor_APP_ID,
            'client_secret': inor_APP_KEY,
            'code': code,
            'redirect_uri': inor_REDIRECT_URI,
            'grant_type': 'authorization_code'
        }
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            # Here, you handle the access token as per your application's logic
            responce_data = response.json() 
            
            access_token = response.json().get('access_token')
            refresh_token = response.json().get('refresh_token')

            # Read the file into memory
            with open(ENV_PATH, 'r') as file:
                lines = file.readlines()

            # Overwrite the variables
            for i, line in enumerate(lines):
                if line.startswith('inor_ACCESS_TOKEN'):
                    lines[i] = f"inor_ACCESS_TOKEN={access_token}\n"
                elif line.startswith('inor_REFRESH_TOKEN'):
                    lines[i] = f"inor_REFRESH_TOKEN={refresh_token}\n"

            # Write the file back out
            with open('.env', 'w') as file:
                file.writelines(lines)
            
            return f"Responce data: {responce_data}"
        else:
            return "Failed to get access token", 400
    else:
        return "No code provided by Inoreader", 400

if __name__ == '__main__':
    webbrowser.open(inor_OAUTH_INIT_SERVER)
    app.run(port=port)
