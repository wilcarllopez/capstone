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


def request_get(url):
    """
    Request and get the url
    :param url: URL provided
    :return soup: parsed text
    """
    try:
        resource = requests.get(url)
        resource.raise_for_status()
        logger.info(f"Successfully established a connection to {url}")
        soup = BeautifulSoup(resource.text, 'lxml')
    except requests.exceptions.ConnectionError:
        logger.error(f"Failed to establish a connection to {url}")
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
    directory = f"{os.path.abspath(os.path.dirname(__name__))}" \
                f"{os.sep}{path}{os.sep}{filename}"
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
        send_to_webservice(directory)


def get_all_downloadable(download_link):
    soup = request_get(download_link)
    name_version = get_details(download_link)
    db.insert_details(username, password, hostname, db_name, name_version)
    download_links = []
    extension = ["zip","exe"]
    for file in soup.find_all("a", {"class": "downloadline"}):
        link = file.get("href")
        if link.split(".")[-1] in extension:
            dl_link = urljoin(download_link, file.get("href"))
            download_links.append(dl_link)
            download_file(dl_link, dl_link.rsplit("/", 1)[-1])

    return downloadable_files


def check_version(download_link):
    """
    Checks the version of the download link
    :param download_link:
    :return:
    """
    name_version = get_details(download_link)
    if db.select_details(username, password, hostname, db_name, name_version):
        logger.info("Found new file, preparing to download")
        get_all_downloadable(download_link)
        return True
    else:
        logger.info("File is updated")
        return False


def get_details(download_link):
    soup = request_get(download_link)
    search_regex = "v[0-9]*\.[0-9]*"
    details = soup.find(text=re.compile(search_regex))
    name_version = details.split("-")[0]
    index = re.search(search_regex, name_version)
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


def get_translations(download_link):
    """

    :param download_link:
    :return:
    """
    global translations
    if download_link not in exemption_link:
        soup = request_get(download_link)
        identifier = soup.find_all("tr", class_="utiltableheader")[-1]
        if identifier is not None:
            table = identifier.find_parent("table")
            row = table.find_all("tr")[1:]  # [1:] to disregard the table header
            translations = []
            for item in row:
                language = item.find_all("td")[0].find("a").get("href")  # [0] first column
                version = item.find_all("td")[-1].text.replace("\n", "")  # [-1] last column
                # link = download_link
                translation_details = {"language": urljoin(download_link, language),
                                       "version": version}
                check_translations(translation_details)
                translations.append(translation_details)
        else:
            pass
        return translations


def get_links(base_url):
    """

    :param base_url:
    :return download_links: List of download links
    """
    soup = request_get(base_url)
    download_links = []
    ul = soup.find("ul")
    for url in ul.find_all("a", href=True, recursive=True):
        if "http" not in url.get('href') \
                and db.select_links(username, password, hostname, db_name, url.get('href')):
            download_link = urljoin(base_url, url.get('href'))
            download_links.append(download_link)
            logger.info(f"Found the download link {download_link}")
            db.insert_links(username, password, hostname, db_name, url.get('href'))

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
    response = requests.post("http://127.0.0.1:5000/safe_files/",
                             files=data)  # POST to the webservice
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
    :return download_links:
    """
    soup = request_get(base_url)
    ul = soup.find("ul")
    download_links = []
    for url in ul.find_all("a", href=True, recursive=True):
        if "http" not in url.get('href') and \
                db.select_links(username, password, hostname, db_name, url.get('href')):
            download_link = urljoin(base_url, url.get('href'))
            logger.info(f"Found the download link {download_link}")
            download_links.append(download_link)  # get details of download pages then save to list
            db.insert_links(username, password, hostname, db_name, url.get('href'))

    for link in download_links:
        check_version(link)
        get_translations(link)
    return download_links


if __name__ == '__main__':
    setup_logging()
    logger = logging.getLogger(__name__)
    config = configparser.ConfigParser()
    path = os.path.abspath(os.path.dirname(__file__))
    config.read(f"{path}{os.sep}config.ini")
    password = config['database']['password']
    hostname = config['database']['hostname']
    username = config['database']['username']
    db_name = config['database']['db_name']
    base_url = config['default']['harvest_url']
    exemption_link = ["http://54.174.36.110/utils/internet_explorer_cookies_view.html"]
    main(base_url)
