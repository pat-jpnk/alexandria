import pytest
import requests
from test_utils import SCHEME, DOMAIN, PORT, api_session, assert_status_code

SCHEME = "http://"
DOMAIN = "127.0.0.1"
PORT = ":5000" 

def pytest_namespace():
    return {"book_id": None}

# TODO: add mocking s3
# add book 
@pytest.mark.dependency()
def test_add_book(api_session):
    path = "/books"
    url = SCHEME + DOMAIN + PORT + path
    params = {
		"release_year": 2004,
		"title": "Testing Book"
	}
    files = {
        "file": open('../tempfiles/test_book.pdf','rb')
    }
    response = api_session.post(url, files=files, json=params)
    assert_status_code(response, 201)


# list single book
@pytest.mark.dependency(depends=["test_add_book"])
def test_add_book(api_session):
    path = "/books/"
    url = SCHEME + DOMAIN + PORT + path
    response = api_session.get(url)
    assert_status_code(response, 200)

# get book file 
@pytest.mark.dependency()
def test_get_book_file(api_session):
    pass


# modify book file
@pytest.mark.dependency()
def test_modify_book_file(api_session):
    pass


# modify book
@pytest.mark.dependency(depends=["test_add_book"])
def test_modify_book(api_session):
    path = "/book/" + pytest.book_id
    url = SCHEME + DOMAIN + PORT + path
    params = {""}
    response = api_session.put(url, json=params)
    assert_status_code(response, 204)
    pytest.book_id = response.json().get("link_id")

# create relation between book and tag 
@pytest.mark.dependency(depends=["test_add_book"])
def test_create_book_tag_relation(api_session):
    pass

# delete relation between book and tag
@pytest.mark.dependency(depends=["test_create_book_tag_relation"])
def test_delete_book_tag_relation(api_session):
    pass

# delete book
@pytest.mark.dependency(depends=["test_add_book"])
def test_delete_book(api_session):
    path = "/book/" + pytest.book_id
    url = SCHEME + DOMAIN + PORT + path
    response = api_session.delete(url)
    assert_status_code(response, 202)