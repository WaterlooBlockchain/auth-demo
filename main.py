# uw_oauth_demo.py
import os, json, base64, hashlib, secrets, requests
from urllib.parse import urlencode
from flask import Flask, redirect, request, session, render_template_string
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

TENANT   = os.environ["TENANT_ID"]
CLIENT   = os.environ["CLIENT_ID"]
SECRET   = os.environ["CLIENT_SECRET"]
SERVER   = os.environ["SERVER_URI"].rstrip("/")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT}/oauth2/v2.0"
SCOPES    = "user.read"

TEMPLATE = """
<!doctype html><title>UW Auth Demo</title>
<h1>{{ title }}</h1>
<pre>{{ data|tojson(indent=2) }}</pre>
<a href="/">home</a>
"""

@app.route("/")
def index():
    return (
        '<h1>UW Auth Demo</h1>'
        '<a href="/login">Sign in with Outlook</a>'
    )

# Microsoft login
@app.route("/login")
def login():
    params = dict(
        client_id     = CLIENT,
        response_type = "code",
        scope         = SCOPES,
        redirect_uri  = f"{SERVER}/authorize",
        state         = secrets.token_urlsafe(16)
    )
    session["oauth_state"] = params["state"]
    return redirect(f"{AUTHORITY}/authorize?{urlencode(params)}")

# Exchange auth code for token then ping Graph API
@app.route("/authorize")
def authorize():
    if request.args.get("state") != session.pop("oauth_state", None):
        return "Invalid state", 400
    code = request.args.get("code")
    if not code:
        return "No code", 400

    token_payload = dict(
        client_id     = CLIENT,
        client_secret = SECRET,
        grant_type    = "authorization_code",
        code          = code,
        redirect_uri  = f"{SERVER}/authorize",
        scope         = SCOPES,
    )

    token = requests.post(f"{AUTHORITY}/token", data=token_payload).json()

    headers = { "Authorization": f"Bearer {token['access_token']}" }
    select  = "department,createdDateTime,userPrincipalName,givenName,surname"
    profile = requests.get(
        f"https://graph.microsoft.com/v1.0/me?$select={select}",
        headers=headers
    ).json()

    uwid = profile["userPrincipalName"].replace("@uwaterloo.ca", "")

    data = dict(
        uwid      = uwid,
        givenName = profile.get("givenName"),
        surname   = profile.get("surname"),
        department= profile.get("department"),
        created   = profile.get("createdDateTime"),
    )

    return render_template_string(TEMPLATE, title="Profile", data=data)

if __name__ == "__main__":
    app.run()
