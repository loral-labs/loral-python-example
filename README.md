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

3. Go to the `localhost:8000/authorize` in your web browser. This will print a URL
