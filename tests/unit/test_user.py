import pytest
import requests
from test_utils import SCHEME, DOMAIN, PORT, api_session, assert_status_code

SCHEME = "http://"
DOMAIN = "127.0.0.1"
PORT = ":5000" 

def pytest_namespace():
    return {"user_id": None}

# login user 
@pytest.mark.dependency()
def test_login_user():
    path = "/login"
    url = SCHEME + DOMAIN + PORT + path
    params = {"user_name": "", "user_password": ""}
    response = api_session.post(url, json=params)
    assert_status_code(response, 200)

# register user ?

# list single user
@pytest.mark.dependency()
def test_list_single_user(api_session):
    path = "/user/" + pytest.user_id
    url = SCHEME + DOMAIN + PORT + path
    response = api_session.get(url)
    assert_status_code(response, 200)

# modify user 
@pytest.mark.dependency()
def test_modify_user(api_session):
    path = "/user/" + pytest.user_id
    url = SCHEME + DOMAIN + PORT + path
    params = {""}
    response = api_session.put(url, json=params)
    assert_status_code(response, 204)
    pytest.user_id = response.json().get("link_id") 

# delete user
@pytest.mark.dependency()
def test_delete_user(api_session):
    path = "/user/" + pytest.user_id
    url = SCHEME + DOMAIN + PORT + path
    response = api_session.delete(url)
    assert_status_code(response, 202)

# logout user 
@pytest.mark.dependency()
def test_logout_user():
    pass