import configparser
import logging
import logging.config
import os
import requests
import sys
import time
import urllib3
import yaml
# absolute imports
from requests import get
from bs4 import BeautifulSoup

def setup_logging(default_path='logging_config.yml', default_level=logging.INFO, env_key='LOG_CFG'):
    """Setting up the logging config"""
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
            except Exception as e:
                print('Error in Logging Configuration. Using default configs', e)
                logging.basicConfig(level=default_level, stream=sys.stdout)
    else:
        logging.basicConfig(level=default_level, stream=sys.stdout)
        print('Failed to load configuration file. Using default configs')
# listUrl = []
# def recursiveUrl(url):
#     page = requests.get(url)
#     soup = BeautifulSoup(page.text, 'html.parser')
#     links = soup.find_all('a')
#     if links is None or len(links) == 0:
#         listUrl.append(url)
#         return 1
#     else:
#         listUrl.append(url)
#         for link in links:
#             if "http" not in link:
#                 fullpath=url + link['href']
#                 recursiveUrl(fullpath)
#             else:
#                 fullpath = url
#                 recursiveUrl(fullpath)
#
# recursiveUrl("http://3.228.218.197/")
# print(listUrl)

def download_files(fullpath):
    url_list=[]
    r = get(base_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find('table',recursive=True)
    links = table.find_all('a', href=True, recursive=True)
    for link in links:
        if ".zip" or ".exe" in link:
            print(link)

def write_to_file(fullpath):
    path = config['default']['path']
    filename = config['default']['filename']
    save_path = f"{path}{os.sep}{filename}"
    with open(save_path, 'w+') as writer:
        writer.write(time.strftime("%Y%m%d-%I%M%S %p"))
        writer.writelines(fullpath)

def main():
    """Main function of the program"""
    config = configparser.ConfigParser()
    path = os.path.abspath(os.path.dirname(__file__))
    config.read(f"{path}{os.sep}config.ini")
    base_url = config['default']['harvest_url']
    try:
        r = get(base_url)
        r.raise_for_status()
        logger.info(f"Successfully established a new connection to {base_url}")
    except requests.exceptions.ConnectionError:
        logger.error(f"Failed to establish a new connection to {base_url}")
        sys.exit(1)
    soup = BeautifulSoup(r.text, 'html.parser')
    counter = 0
    download_links = []
    url_list = soup.find('ul')
    for a in url_list.find_all('a', href=True, recursive=True):
        if "nirsoft" not in str(a['href']):
            if "http" not in str(a['href']):
                fullpath = str(base_url + a['href'])
                counter += 1
            else:
                fullpath = a['href']
                counter += 1
            logger.info(f"{counter} - {fullpath}")
            download_files(fullpath)
            write_to_file(fullpath)
            download_links.append(fullpath) #appends the url to a list
    return download_links
if __name__ == '__main__':
    setup_logging()
    logger = logging.getLogger(__name__)
    config = configparser.ConfigParser()
    path = os.path.abspath(os.path.dirname(__file__))
    config.read(f"{path}{os.sep}config.ini")
    base_url = config['default']['harvest_url']
    main()
    # download_files(base_url)
