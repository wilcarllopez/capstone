import requests

from requests import get

import re

import configparser

import os

from bs4 import BeautifulSoup

from urllib.parse import urljoin

import db_manage as db

config = configparser.ConfigParser()

conf_dir = os.path.join(os.path.dirname(__file__), 'conf.ini')

config.read(conf_dir)

password = config['args']['password']

hostname = config['args']['hostname']

username = config['args']['username']

dbname = config['args']['dbname']


def parse_link(link):
    url = link

    resource = requests.get(url)

    soup = BeautifulSoup(resource.text, 'lxml')

    return soup


def download_file(url, filename):
    with open("{}{}{}{}{}".format(os.path.abspath(os.path.dirname(__name__)), os.sep, "downloads", os.sep, filename),
              "wb") as file:
        response = get(url)

        file.write(response.content)


def get_all_downloadable(download_page_link):
    soup = parse_link(download_page_link)

    name_version = get_details(download_page_link)

    db.insert_details(username, password, hostname, dbname, name_version)

    download_links = soup.find_all("a", {"class": "downloadline"})

    # download_links = soup.find_all("a", href=True)

    acceptable_ext = ["exe", "zip"]

    downloadable_files = []

    for file in download_links:

        file_link = file.get("href")

        if file_link.split(".")[-1] in acceptable_ext:
            download_link = urljoin(download_page_link, file_link)

            downloadable_files.append(download_link)

            download_file(download_link, download_link.rsplit("/", 1)[-1])

            print(download_link)

    return downloadable_files


def check_version(download_page_link):
    name_version = get_details(download_page_link)

    if db.select_details(username, password, hostname, dbname, name_version):

        get_all_downloadable(download_page_link)

        return True

    else:

        return False


def get_details(download_page_link):
    soup = parse_link(download_page_link)

    version_regex = "v[0-9]*\.[0-9]*"

    details = soup.find(text=re.compile(version_regex))

    name_version = details.split("-")[0]

    index = re.search(version_regex, name_version)

    name = name_version[0:index.start()].replace("\n", "")

    version = name_version[index.start():].replace("\n", "")

    return {"name": name, "version": version}


def check_translations(translations):
    if db.select_translations(username, password, hostname, dbname, translations):
        download_link = translations['language']

        version = translations['version']

        download_file(download_link, version + download_link.rsplit("/", 1)[-1])

        db.insert_translations(username, password, hostname, dbname, translations)


def get_translations(download_page_link):
    different_link = ["http://54.174.36.110/utils/internet_explorer_cookies_view.html"]

    if download_page_link not in different_link:

        soup = parse_link(download_page_link)

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


def get_links():
    base_url = "http://54.174.36.110/"

    soup = parse_link(base_url)

    unordered_list = soup.find("ul")

    index_links = unordered_list.find_all("a", href=True)

    download_pages = []

    for link in index_links:

        href = link.get("href")

        if "http" not in href and db.select_links(username, password, hostname, dbname, href):
            download_page_link = urljoin(base_url, href)  # url of the download page

            download_pages.append(download_page_link)  # get details of download pages then save to list

            # check_version(download_page_link)  # checker of version changes

            db.insert_links(username, password, hostname, dbname, href)  # checker of link duplicates

    for pages in download_pages:
        check_version(pages)

        get_translations(pages)

    return download_pages


def main():
    get_links()

    # download_file("http://54.174.36.110/utils/trans/webbrowserpassview_arabic.zip" ,"trail.zip")

    # get_translations("http://54.174.36.110/utils/iehv.html")


if __name__ == '__main__':
    main()
