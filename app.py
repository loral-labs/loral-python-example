import json
import os
from fastapi import FastAPI, Request, Depends, HTTPException
import httpx
from base64 import b64encode

# Initialize the FastAPI app
app = FastAPI()

# Constants for Loral OAuth
REDIRECT_URI = 'http://localhost:8000/callback'
SCOPE = 'kroger'
STATE = json.dumps({
    "userId": "12345",
    "csrf": "12345",
})

# Helper function to encode client credentials
def encode_credentials(client_id: str, client_secret: str) -> str:
    credentials = f"{client_id}:{client_secret}"
    return b64encode(credentials.encode()).decode()

@app.on_event("startup")
async def startup():
    api_url = f"https://api.loral.dev/client/create"
    data = {
        'name': "grocery_client",
        'redirect_uris': [REDIRECT_URI],
        'scopes': ["kroger"]
    }
    if os.path.exists("loral_client.json"):
        with open("loral_client.json", "r") as f:
            client_info = json.load(f)
            os.environ["LORAL_CLIENT_ID"] = client_info['id']
            os.environ["LORAL_CLIENT_SECRET"] = client_info['secret']
            return
    async with httpx.AsyncClient() as client:
        response = await client.post(api_url, json=data)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Loral unable to create client\n" + response.text)
        print("Client created!")
        client_info = response.json()
        with open("loral_client.json", "w") as f:
            json.dump(client_info, f)
        os.environ["LORAL_CLIENT_ID"] = client_info['id']
        os.environ["LORAL_CLIENT_SECRET"] = client_info['secret']
        return
    

# Authorization endpoint
@app.get("/authorize")
async def authorize():
    auth_url = (
        f"https://auth.loral.dev/oauth2/auth"
        f"?client_id={os.getenv('LORAL_CLIENT_ID')}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope={SCOPE}"
        f"&state={STATE}"  # The state should be a unique token generated per request
    )
    return auth_url

# Callback endpoint for receiving the authorization code
@app.get("/callback")
async def callback(code: str, state: str):
    # new_state = json.loads(state)
    # old_state = json.loads(STATE)  
    # if (new_state["userId"] != old_state["userId"]) or (new_state["csrf"] != old_state["csrf"]):
    #     raise HTTPException(status_code=400, detail="Invalid CSRF token")
    token_url = "https://auth.loral.dev/oauth2/token"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f"Basic {encode_credentials(os.getenv('LORAL_CLIENT_ID'), os.getenv('LORAL_CLIENT_SECRET'))}",
    }
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, headers=headers, data=data)
        tokens = response.json()
        print(tokens)
        os.environ["LORAL_ACCESS_TOKEN"] = tokens['access_token']
        os.environ["LORAL_REFRESH_TOKEN"] = tokens.get('refresh_token', "")
        return "Tokens created!"

# Refresh token endpoint
@app.post("/refresh_token")
async def refresh_token():
    token_url = "https://auth.loral.dev/oauth2/token"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f"Basic {encode_credentials(os.getenv('LORAL_CLIENT_ID'), os.getenv('LORAL_CLIENT_SECRET'))}",
    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': os.getenv("LORAL_REFRESH_TOKEN"),
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, headers=headers, data=data)
        new_tokens = response.json()
        os.environ["LORAL_ACCESS_TOKEN"] = new_tokens['access_token']
        os.environ["LORAL_REFRESH_TOKEN"] = new_tokens['refresh_token']
        return "Tokens refreshed!"

@app.get("/grocery_search")
async def grocery_search(search_term: str):
    api_url = f"https://api.loral.dev/kroger/execute/v1/products?filter.term={search_term}"
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, headers={"Authorization": f"Bearer {os.getenv('LORAL_ACCESS_TOKEN')}"})
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Loral unable to execute request\n" + response.text)
        return response.json()

@app.get("/grocery_auth")
async def grocery_auth():
    api_url = "https://api.loral.dev/kroger/auth"
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, params={"redirect_uri": "http://localhost:8000/grocery_auth"}, headers={"Authorization": f"Bearer {os.getenv('LORAL_ACCESS_TOKEN')}"})
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Loral unable to execute request\n" + response.text)
        return response.text