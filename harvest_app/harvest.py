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
        logger.info(f"Downloaded {filename}")
        send_to_webservice(directory)


def get_all_downloadable(download_link):
    """
    Get all
    :param download_link:
    :return:
    """
    soup = request_get(download_link)
    name_version = get_details(download_link)
    db.insert_details(username, password, hostname, port, db_name, name_version)
    download_links = []
    for tag in soup.select('a.downloadline'):
        if tag['href'].endswith(('.zip', '.exe')):
            download_links.append(urljoin(download_link, tag['href']))
    for link in download_links:
        download_file(link, link.split("/")[-1])
    return download_links


def check_version(download_link):
    """
    Checks the version of the download link
    :param download_link:
    :return:
    """
    name_version = get_details(download_link)
    if db.select_details(username, password, hostname, port, db_name, name_version):
        get_all_downloadable(download_link)
        return True
    else:
        return False


def get_details(download_link):
    soup = request_get(download_link)
    downloads = []
    string = soup.find(string=re.compile('v[0-9]*\.[0-9]*'))
    try:
        search = re.search(re.compile('v[0-9]*\.[0-9]*'), string)
        version = search.group(0)
        name = string[:search.start()]
        for tag in soup.select('a.downloadline'):
            if tag['href'].endswith(('.zip', '.exe')):
                downloads.append(urljoin(download_link, tag['href']))
        return {'name': name.strip(),
                'version': version[1:].strip(),
                'url': downloads}
    except TypeError as err:
        logger.error(err)
        pass


def check_translations(translations):
    """

    :param translations:
    :return:
    """
    if db.select_translations(username, password, hostname, port, db_name, translations):
        download_link = translations['language']
        version = translations['version']
        download_file(download_link, download_link.rsplit('/', 1)[-1])
        db.insert_translations(username, password, hostname, port, db_name, version)


def get_translations(download_link):
    """
    Get all translations details
    :param download_link:
    :return:
    """
    soup = request_get(download_link)
    translations = []
    try:
        table = soup.select('tr.utiltableheader')[-1].find_parent('table')
        table_rows = table.find_all('tr')[1:]
        for row in table_rows:
            table_data = row.find_all('td')
            try:
                translation = table_data[0].select_one('a')['href'].split('/')[-1]
                translation_version = table_data[-1].text.strip()
                link = urljoin(download_link, row.contents[0].next['href'])
                translations.append({'translation': translation,
                                     'translation_version': translation_version,
                                     'link': link})
            except TypeError as err:
                logger.error(err)
        return translations
    except IndexError:
        pass


def send_to_webservice(directory):
    """
    Sends the downloaded file to the web-service
    :param directory: Path directory of the downloaded files
    :return response.status_code: 200 if succeeds
    """
    file = os.path.basename(directory)
    data = {"file": (file, open(directory, 'rb'))}
    logger.info(f"Uploading file {file} to web service API")
    response = requests.post(f"http://{hostname}:{api_port}/safe_files/",
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
        link = url.get('href')
        if "http" not in link and db.select_links(username, password, hostname, port, db_name, link):
            download_link = urljoin(base_url, link)
            logger.info(f"Found the download link {download_link}")
            download_links.append(download_link)
            db.insert_links(username, password, hostname, port, db_name, link)
        else:
            logger.info("No new download_links")
            pass

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

    base_url = config['default']['harvest_url']
    password = config['database']['password']
    hostname = config['database']['hostname']
    username = config['database']['username']
    port = config['database']['port']
    api_port = config['webservice']['port']
    db_name = config['database']['db_name']
    main("http://nirsoft.net")
