import pytest
import requests
from test_utils import SCHEME, DOMAIN, PORT, api_session, assert_status_code

SCHEME = "http://"
DOMAIN = "127.0.0.1"
PORT = ":5000" 

def pytest_namespace():
    return {"book_id": None}