# generate_token.py
# FINAL, ROBUST VERSION using the fundamental auth flow.

import os
from google_auth_oauthlib.flow import Flow

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

def generate_token():
    """
    Runs a manual, two-step OAuth 2.0 flow.
    1. Generates and displays an authorization URL.
    2. User authorizes in a browser and pastes the redirect URL back.
    3. The script extracts the authorization code and fetches the token.
    """
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"\nERROR: '{CREDENTIALS_FILE}' not found. Please place it here.\n")
        return

    # Use the core Flow object for maximum control
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob' # 'Out-of-band' for console apps
    )

    # 1. Generate the authorization URL
    auth_url, _ = flow.authorization_url(prompt='consent')

    print('--- Google Authentication ---')
    print('Please visit this URL to authorize this application:')
    print(auth_url)
    print('-' * 20)

    # 2. Get the authorization code from the user
    code = input('Enter the authorization code from your browser here: ')

    # 3. Exchange the code for a token
    try:
        flow.fetch_token(code=code)
        creds = flow.credentials
        
        # Save the credentials for the application to use
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
            
        print(f"\nSuccess! Credentials saved to '{TOKEN_FILE}'.")
        print("You can now upload this token.json file to the server.\n")

    except Exception as e:
        print(f"\nError fetching token: {e}\n")


if __name__ == '__main__':
    generate_token()