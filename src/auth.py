import os
import google_auth_oauthlib.flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scopes required for Gmail IMAP and SMTP (if needed later)
SCOPES = ['https://mail.google.com/']

def get_flow(client_secret_file, redirect_uri):
    """Creates an OAuth flow instance."""
    return google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        client_secret_file,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )

def get_auth_url(client_secret_file, redirect_uri):
    """Generates the authorization URL."""
    flow = get_flow(client_secret_file, redirect_uri)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    return authorization_url, state

def get_credentials_from_code(client_secret_file, redirect_uri, code):
    """Exchanges the auth code for credentials."""
    flow = get_flow(client_secret_file, redirect_uri)
    flow.fetch_token(code=code)
    return flow.credentials
