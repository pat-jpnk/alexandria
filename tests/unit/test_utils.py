import pytest
import requests

SCHEME = "http://"
DOMAIN = "127.0.0.1"
PORT = ":5000" 

def assert_status_code(response, expected_code):
    assert response.status_code == expected_code, "expected {}, but got {} ".format(expected_code, response.status_code)

@pytest.fixture(scope="session")
def api_session():
    path = "/login"
    url = SCHEME + DOMAIN + PORT + path
    params = {"user_name": "testUser", "user_password": "testPassword"}
    response = requests.post(url, json=params)
    assert_status_code(response, 200)
    session = requests.Session()
    session.headers.update({"Authorization": "Bearer {}".format(response.json().get("access_token"))})
    yield session