import configparser
import db_manage.py
import logging
import logging.config
import os
import re
import requests
import sys as sys
import yaml
# absolute imports
from bs4 import BeautifulSoup


def link_details(url):
    """
    Get the application's name and version
    :param url: Download link
    :return: app_name, version
    """
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    details = soup.find(text=re.compile("v[0-9]*\.[0-9]*"))
    index = re.search("v[0-9]*\.[0-9]*", details.split("-")[0])
    app_name = details.split("-")[0][0:index.start()].replace("\n", "")
    app_version = details.split("-")[0][index.start():].replace("\n", "")
    return app_name, app_version


def download_files(url):
    """
    :param url: Download link
    :return:
    """
    url_list = []
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    td = soup.find('td', recursive=True)
    links = td.find_all("a", class_="downloadline", href=True)
    for link in links:
        print(link)
        url_list.append(link)
    for link in url_list:
        print(link)


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


def write_to_file(fullpath):
    """
    Write a list of download links to a text file
    :param fullpath: Downloadable links
    :return:
    """
    path = config['default']['path']
    filename = config['default']['filename']
    save_path = f"{path}{os.sep}{filename}"
    with open(save_path, 'a+') as writer:
        writer.write(fullpath + "\n")


def main(base_url):
    """
    Main function of the program: collects downloadable links
    :param base_url: Mirror link of Nirsoft.net
    :return: List of downloadable links
    """
    try:
        r = requests.get(base_url)
        r.raise_for_status()
        logger.info(f"Successfully established a new connection to {base_url}")
    except requests.exceptions.ConnectionError:
        logger.error(f"Failed to establish a new connection to {base_url}")
        sys.exit(1)
    soup = BeautifulSoup(r.text, 'html.parser')
    counter = 0
    download_links = []
    auxiliary_list = []
    url_list = soup.find('ul')

    """Checks for download links"""
    for url in url_list.find_all('a', href=True, recursive=True):
        if "nirsoft" not in str(url['href']):
            if "http" not in str(url['href']):
                fullpath = str(base_url + url['href'])
            else:
                fullpath = url['href']
            logger.info(f"Found the link: {fullpath}")
            # download_files(fullpath)
            download_links.append(fullpath)  # appends the url to a list

    """Getting the unique value of download links"""
    for link in download_links:
        if link not in auxiliary_list:
            auxiliary_list.append(link)
            counter += 1
            logger.info(f"{counter} - {link} appended to the final list")

    for link in auxiliary_list:
        link_details(link)
        # write_to_file(link)
        download_files(link)
        # write_to_db()

    return auxiliary_list


if __name__ == '__main__':
    setup_logging()
    logger = logging.getLogger(__name__)
    config = configparser.ConfigParser()
    path = os.path.abspath(os.path.dirname(__file__))
    config.read(f"{path}{os.sep}config.ini")
    base_url = config['default']['harvest_url']
    main(base_url)
