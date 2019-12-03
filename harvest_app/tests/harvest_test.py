import requests
from bs4 import BeautifulSoup

url = "http://54.174.36.110/"


def test_request_url():
    resource = requests.get(url)
    resource.raise_for_status()
    assert BeautifulSoup(resource.text, 'lxml')

if __name__ == '__main__':
    pytest.main()