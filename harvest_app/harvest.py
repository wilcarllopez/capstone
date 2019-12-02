import configparser
import logging
import logging.config
import requests
import re
import os
import db_manage as db
import sys
import yaml
# absolute imports
from bs4 import BeautifulSoup
from requests import get
from urllib.parse import urljoin

config = configparser.ConfigParser()
path = os.path.abspath(os.path.dirname(__file__))
config.read(f"{path}{os.sep}config.ini")
password = config['database']['password']
hostname = config['database']['hostname']
username = config['database']['username']
db_name = config['database']['db_name']


def request_get(url):
    """
    Request and get the url
    :param url: URL provided
    :return soup: parsed text
    """
    try:
        resource = requests.get(url)
        resource.raise_for_status()
        logger.info(f"Successfully established a new connection to {url}")
        soup = BeautifulSoup(resource.text, 'lxml')
    except requests.exceptions.ConnectionError:
        logger.error(f"Failed to establish a new connection to {url}")
        sys.exit(1)
    return soup


def download_file(url, filename):
    """
    Downloads the file from the download links
    :param url: Download url
    :param filename: Filename
    :return:
    """
    path = config['download']['path']
    directory = f"{os.path.abspath(os.path.dirname(__name__))}{os.sep}{path}{os.sep}{filename}"
    response = get(url)
    if os.path.exists(directory):
        logger.info("File already exists")
        pass
    else:
        logger.info(f"Downloading file {filename} from {url}")
        with open(directory, 'wb') as file:
            file.write(response.content)
        logger.info("Download complete")
        logger.info("Uploading downloaded files to webservice")
        send_to_webservice(directory, filename)


def get_all_downloadable(download_page_link):
    soup = request_get(download_page_link)
    name_version = get_details(download_page_link)
    db.insert_details(username, password, hostname, db_name, name_version)
    download_links = []
    extension = ["exe", "zip"]
    for link in soup.find_all("a", href=True):
        if "http" not in link.get('href'):
            for ext in extension:
                if ext in link.get('href'):
                    download_links.append(link.get('href'))
    # download_links = soup.find_all("a", href=True)

    downloadable_files = []
    for file in download_links:
        file_link = file.get("href")
        if file_link.split(".")[-1] in extension:
            download_link = urljoin(download_page_link, file_link)
            downloadable_files.append(download_link)
            download_file(download_link, str(download_link.split("/")[-1]))

    return downloadable_files


def check_version(download_page_link):
    """
    Checks the version of the download link
    :param download_page_link:
    :return:
    """
    name_version = get_details(download_page_link)
    if db.select_details(username, password, hostname, db_name, name_version):
        logger.info("Found new file, preparing to download")
        get_all_downloadable(download_page_link)
        return True
    else:
        logger.info("File is updated")
        return False


def get_details(download_page_link):
    soup = request_get(download_page_link)
    details = soup.find(text=re.compile("v[0-9]*\.[0-9]*"))
    name_version = details.split("-")[0]
    index = re.search("v[0-9]*\.[0-9]*", name_version)
    name = name_version[0:index.start()].replace("\n", "").rsplit()
    version = name_version[index.start():].replace("\n", "").rsplit()
    return {"name": name, "version": version}


def check_translations(translations):
    """

    :param translations:
    :return:
    """
    if db.select_translations(username, password, hostname, db_name, translations):
        download_link = translations['language']
        version = translations['version']
        download_file(download_link, download_link.rsplit('/', 1)[-1])
        db.insert_translations(username, password, hostname, db_name, version)
    return True


def get_translations(download_page_link):
    """

    :param download_page_link:
    :return:
    """
    different_link = ["http://54.174.36.110/utils/internet_explorer_cookies_view.html"]
    if download_page_link not in different_link:
        soup = request_get(download_page_link)
        identifier = soup.find_all("tr", class_="utiltableheader")[-1]
        table = identifier.find_parent("table")
        row = table.find_all("tr")[1:]  # [1:] to disregard the table header
        translations = []
        for item in row:
            language = item.find_all("td")[0].find("a").get("href")
            version = item.find_all("td")[-1].text.replace("\n", "")
            translation_details = {"language": urljoin(download_page_link, language), "version": version}
            check_translations(translation_details)
            translations.append(translation_details)
        return translations


def get_links(base_url):
    """

    :param base_url:
    :return:
    """
    soup = request_get(base_url)
    ul = soup.find("ul")
    download_links = []
    auxiliary_links = []
    for url in ul.find_all("a", href=True, recursive=True):
        if "nirsoft" not in str(url['href']):
            if "http" not in url['href'] and db.select_links(username, password, hostname, db_name, url['href']):
                fullpath = str("{}{}".format(base_url, url['href']))  # url of the download page
            else:
                fullpath = str("{}{}".format(base_url, url['href']))
            logger.info(f"Found the download link {fullpath}")
            auxiliary_links.append(fullpath)  # get details of download pages then save to list
            # checker of link duplicates

    for link in auxiliary_links:
        if link not in download_links:
            download_links.append(link)
            logger.info(f"{link} appended to the final list of download links")
            db.insert_links(username, password, hostname, db_name, link)

    for link in download_links:
        check_version(link)
        get_translations(link)
    return download_links

def send_to_webservice(directory):
    """
    Sends the downloaded file to the web-service
    :param directory: Path directory of the downloaded files
    :return response.status_code: 200 if succeeds
    """
    file = os.path.basename(directory)
    data = {"file": (file, open(directory, 'rb'))}
    response = requests.post("", files=data) # INSERT URL
    logger.info(f"Response: {response.status_code}")
    return response.status_code

def setup_logging(default_path='logging_config.yml', default_level=logging.INFO, env_key='LOG_CFG'):
    """
    Seting up logging config
    :param default_path:
    :param default_level:
    :param env_key:
    :return:
    """
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


def main(base_url):
    """
    Main function of the program
    :param base_url: URL to crawl
    :return True:
    """
    get_links(base_url)
    return True


if __name__ == '__main__':
    setup_logging()
    logger = logging.getLogger(__name__)
    base_url = config['default']['harvest_url']
    main(base_url)
