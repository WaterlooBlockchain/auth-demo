# auth-demo

This is a minimal Flask app that demonstrates how to authenticate with Microsoft Entra ID, then call the Microsoft Graph API (`/me`) to fetch a user’s profile.

---

## Features

- Redirects to Microsoft login (`/login`)
- Handles the callback (`/authorize`)
- Exchanges the authorization code for an access token
- Calls the Graph API to display requested profile fields

---

## Prerequisites

- Python 3.10+
- A registered App Registration in Azure Entra ID
- The following values from your app registration:
  - `TENANT_ID`
  - `CLIENT_ID`
  - `CLIENT_SECRET`
  - `SERVER_URI` (Must match redirect URI set in Azure)
