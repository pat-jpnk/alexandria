import pytest
import requests
from assertion import assert_status_code

# TODO: create test_DB script with test user for authentication

SCHEME = "http://"
DOMAIN = "127.0.0.1"
PORT = ":5000" 

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


def pytest_namespace():
    return {"tag_id": None}


# add tag
@pytest.mark.dependency()
def test_add_tag(api_session):
    path = "/tags"
    url = SCHEME + DOMAIN + PORT + path
    params = {"tag": "tag1"}    
    #response = requests.post(url, json=params)
    response = api_session.post(url, json=params)
    assert_status_code(response, 201)
    pytest.tag_id = response.json().get("link_id") 



# list single tag
@pytest.mark.dependency(depends=["test_add_tag"])
def test_list_single_tag(api_session):
    path = "/tag/" + pytest.tag_id
    url = SCHEME + DOMAIN + PORT + path
    response = requests.get(url)
    assert_status_code(response, 200)


# modify tag
@pytest.mark.dependency(depends=["test_list_single_tag"])
def test_modify_tag(api_session):
    path = "/tag/" + pytest.tag_id
    url = SCHEME + DOMAIN + PORT + path
    params = {"tag": "tag2"}
    response = requests.put(url, json=params)
    assert_status_code(response, 204)

# delete tag
@pytest.mark.dependency(depends=["test_modify_tag"])
def test_delete_tag(api_session):
    path = "/tag/" + pytest.tag_id
    url = SCHEME + DOMAIN + PORT + path
    response = requests.delete(url)
    assert_status_code(response, 202)