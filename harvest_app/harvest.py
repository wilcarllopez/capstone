import configparser
import db_manage
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
    soup = request_get(url)
    details = soup.find(text=re.compile("v[0-9]*\.[0-9]*"))
    logger.info(f"Getting download link details from {url}")
    if details is None:
        row = ("","")
        pass
    else:
        index = re.search("v[0-9]*\.[0-9]*", details.split("-")[0])
        app_name = details.split("-")[0][0:index.start()].replace("\n", "")
        app_version = details.split("-")[0][index.start():].replace("\n", "")
        row = [app_name, app_version]
    find_translations(url)
    # for link in row:
    # save_to_db(link)

    logger.info(row)


def find_translations(link):
    soup = request_get(link)
    try:
        identifier = soup.find_all("tr", class_="utiltableheader")[-1]
        table = identifier.find_parent("table")
        row = table.find_all("tr")[1:]  # [1:] to disregard the table header
        translations = []
        for item in row:
            language = item.find_all("td")[0].find("a").get("href")
            version = item.find_all("td")[-1].text.replace("\n", "")
            translation_details = {"language": urljoin(link, language), "version": version}
            logger.info(translation_details)
            check_translations(translation_details)
            translations.append(translation_details)
    except:
        translations = None
    return translations

def download_files(url):
    """
    :param url: Download link
    :return url_list: List of download links
    """
    soup = request_get(url)
    suffix = ["zip", "exe"]
    # for link in soup.find_all("a", href=True):
    #     if "http" not in link.get('href'):
    #         for suff in suffix:
    #             if suff in link.get('href'):
    #                 print(link)
    url_list = [a['href'] for suff in suffix for a in soup.find_all('a', href=True)
                if "http" or "html" not in a.get('href') if suff in a.get('href')]
    for link in url_list:
        find_translations(link)

def get_download_files(url_list, base_url):
    path = config['download']['path']
    for link in url_list:
        if "trans" in link:
            r = requests.get(f"{base_url}/utils/{link}")
            logger.info(f"Downloading file from: {base_url}/utils/{link}")
            filename = link.split("/")[-1]
            directory = f"{os.path.abspath(os.path.dirname(__name__))}{os.sep}{path}{os.sep}{filename}"
            if os.path.exists(directory):
                logger.info("File already exists")
                pass
            else:
                with open(directory, 'wb') as f:
                    f.write(r.content)
        else:
            link = link.replace("..", "")
            r = requests.get(f"{base_url}{link}")
            logger.info(f"Downloading file from: {base_url}{link}")
            filename = link.split("/")[-1]
            directory = f"{os.path.abspath(os.path.dirname(__name__))}{os.sep}{path}{os.sep}{filename}"
            if os.path.exists(directory):
                logger.info("File already exists")
                pass
            else:
                with open(directory, 'wb') as f:
                    f.write(r.content)


def save_to_db(row):
    db_manage.write_to_db(str(row), config['database']['db_name'], config['database']['username'],
                          config['database']['hostname'])


def request_get(url):
    """
    Request and get the url
    :param url: URL provided
    :return soup: parsed text
    """
    try:
        r = requests.get(url)
        r.raise_for_status()
        logger.info(f"Successfully established a new connection to {url}")
        soup = BeautifulSoup(r.text, 'lxml')
    except requests.exceptions.ConnectionError:
        logger.error(f"Failed to establish a new connection to {url}")
        sys.exit(1)
    return soup


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
    soup = request_get(base_url)
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
        # get_download_files(link, base_url)

        link_details(link)
        # write_to_file(link)
        # download_files(link)
        # write_to_db()

    return auxiliary_list


if __name__ == '__main__':
    setup_logging()
    logger = logging.getLogger(__name__)
    config = configparser.ConfigParser()
    path = os.path.abspath(os.path.dirname(__file__))
    config.read(f"{path}{os.sep}config.ini")
    base_url = "https://www.nirsoft.net/"
    main(base_url)

