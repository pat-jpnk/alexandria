import pytest
import requests
from test_utils import DOMAIN, PORT, SCHEME, api_session, assert_status_code

import resources.tag as tag

# TODO: create test_DB script with test user for authentication

def pytest_namespace():
    return {"tag_id": None}


# add tag
@pytest.mark.dependency()
def test_add_tag(api_session):
    path = "/tags"
    url = SCHEME + DOMAIN + PORT + path
    params = {"tag": "tag1"}    
    response = api_session.post(url, json=params)
    assert_status_code(response, 201)
    pytest.tag_id = response.json().get("link_id") 



# list single tag
@pytest.mark.dependency(depends=["test_add_tag"])
def test_list_single_tag(api_session):
    path = "/tag/" + pytest.tag_id
    url = SCHEME + DOMAIN + PORT + path
    response = api_session.get(url)
    assert_status_code(response, 200)


# modify tag
@pytest.mark.dependency(depends=["test_add_tag"])
def test_modify_tag(api_session):
    path = "/tag/" + pytest.tag_id
    url = SCHEME + DOMAIN + PORT + path
    params = {"tag": "tag2"}
    response = api_session.put(url, json=params)
    assert_status_code(response, 204)
    pytest.tag_id = response.json().get("link_id") 


# delete tag
@pytest.mark.dependency(depends=["test_add_tag"])
def test_delete_tag(api_session):
    path = "/tag/" + pytest.tag_id
    url = SCHEME + DOMAIN + PORT + path
    response = api_session.delete(url)
    assert_status_code(response, 202)
