import requests
import json
import uuid

url = "https://rpo5z5k20l.execute-api.us-east-2.amazonaws.com/prod/URLS"
url_id = str(uuid.uuid4)


def test_http_post_method():
    website = {"URL_ID": url_id, "website": "www.google.com"}
    r = requests.post(url, data=json.dumps(website))
    assert r.status_code == 200


def test_http_get_method():
    r = requests.get(url)
    assert r.status_code == 200


def test_http_patch_method():
    website = {"URL_ID": url_id, "website": "www.twitter.com"}
    r = requests.patch(url, data=json.dumps(website))
    assert r.status_code == 200


def test_http_delete_method():
    website = {"URL_ID": url_id}
    r = requests.delete(url, data=json.dumps(website))
    assert r.status_code == 200
