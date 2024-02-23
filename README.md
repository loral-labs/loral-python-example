# loral-python-example

This is a Python example server that interacts with the Loral service for authorization. 

## Usage

1. Clone the repository and install the required dependencies.

```bash
pip install -r requirements.txt
```

2. Run the FastAPI server
```bash
uvicorn app:app --reload
```

3. Go to the `localhost:8000/authorize` in your web browser. This will print a URL.

4. Follow that URL and then either create a Loral account or sign in with your existing Loral account. You should then see a page asking you to authorize **grocery_search** to your kroger scope. After this is done, you should see "Tokens created!" printed in your browser.

5. Now go to `localhost:8000/grocery_auth` in your browser. You will then see a Kroger url that you should follow. Follow that and then either create or enter your Kroger account credentials. 

6. Lastly, go to `localhost:8000/grocery_search?search_term={{SEARCH_TERM}}` where SEARCH_TERM is whatever search term you want to search through the Kroger website.
