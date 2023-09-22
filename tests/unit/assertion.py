def assert_status_code(response, expected_code):
    assert response.status_code == expected_code, "expected {}, but got {} ".format(expected_code, response.status_code)
    