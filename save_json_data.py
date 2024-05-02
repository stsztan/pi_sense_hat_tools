from bs4 import BeautifulSoup
import cachetools.func
import datetime
import logging
import logging.config
import pathlib
import random
import os
import requests
import sys
import time
import urllib.request, urllib.error, urllib.parse
import yaml
from utils.auto_config_params_handler import auto_param_config


DEV_MACHINE = auto_param_config('-m', '--dev_machine',
                                help='development machine or platform')


def is_dev():
    return sys.platform == DEV_MACHINE


data_folder = auto_param_config('-d', '--data_folder',
                                help='data folder saving json')
default_encoding = auto_param_config('-e', '--encodings',
                                     help='default text/json encoding')
min_ttl = 10 if is_dev() else 10 * 25
max_ttl = 30 if is_dev() else 10 * 65
max_pages = 1  # limiting max. pages query
sub_s_min = 1 if is_dev() else 5
sub_s_max = 2 if is_dev() else 15
pg_s_min = 3 if is_dev() else 10
pg_s_max = 5 if is_dev() else 30
w_min = 1 if is_dev() else 25
w_max = 2 if is_dev() else 85
selenium_min = 1 if is_dev() else 5
selenium_max = 10 if is_dev() else 25


try:
    with open('config.yml', 'r') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
except:
    logging.basicConfig(format='[%(levelname)s] %(process)d <%(name)s> '
                        '%(asctime)s | %(message)s', level=logging.DEBUG)

logger = logging.getLogger(__name__)


@cachetools.func.ttl_cache(maxsize=128, ttl=random.randrange(min_ttl, max_ttl))
def get_now_milis():
    fetch_url(root_url)
    time.sleep(random.randrange(selenium_min, selenium_max))
    fetch_url(base_url)
    return str(round(
        datetime.datetime.timestamp(datetime.datetime.now())*1000))


def get_base_url():
    millis = get_now_milis()
    partial_url = auto_param_config('-p', '--partial_url',
                                    help='partial url api')
    return f'{partial_url}{millis}'


root_url = auto_param_config('-r', '--url_root', help='url domain root')
base_url = auto_param_config('-b', '--url_base', help='base fetch url')
user_agent = auto_param_config('-u', '--user_agent',
                               help='fetch user agent text')


req = {
 "headers": {
     "User-Agent": user_agent,
     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
     "Accept-Language": "en-US,en;q=0.5",
     "Upgrade-Insecure-Requests": "1",
     "Sec-Fetch-Dest": "document",
     "Sec-Fetch-Mode": "navigate",
     "Sec-Fetch-Site": "same-origin",
     "Sec-Fetch-User": "?1"
 },
 "referrer": root_url,
 "method": "GET",
 "mode": "cors"
}


def get_abs_path(file_name):
    date_folder = urllib.parse.quote(
        str(datetime.date.today().isoformat()),
        safe='')
    base_folder = pathlib.Path.joinpath(
            pathlib.Path(
                os.getcwd()),
            pathlib.Path(data_folder))
    subfolder = pathlib.Path.joinpath(
            base_folder,
            pathlib.Path(date_folder))
    return pathlib.Path.joinpath(
        subfolder,
        file_name)


def createAndOpen(file_path, mode, encoding=default_encoding):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        return open(file_path, mode, encoding=encoding)
    except OSError as io_error:
        logger.exception(f'Error creating {str(file_path)} '
                         f'directory structure or file: {str(io_error)}')


def fetch_url(url: str):
    try:
        logger.info(f'Fetching: {url}')
        response = requests.get(url, headers=req['headers'])
        html_content = response.content.decode(default_encoding)
        return html_content
    except urllib.error.HTTPError as e:
        logger.exception(str(e))
        return e


def save_html(html: str, url=''):
    safe_url = urllib.parse.quote(url, safe='')
    current_time = datetime.datetime.now().strftime('%Y-%m-%dT%H.%M.%S_%f%z')
    file_name = f'{safe_url}-{current_time}.html'
    file_path = get_abs_path(file_name)
    logger.info(file_path)
    try:
        with createAndOpen(file_path, 'w', encoding=default_encoding) as exchange_file:
            exchange_file.write(html)
        return str(file_path)
    except OSError as e:
        logger.exception(str(e))


def save_json(json_content: str, file_name: str, ext: str = 'json'):
    time_str = datetime.datetime.now().strftime('%Y-%m-%dT%H.%M.%S_%f%z')
    file_path = get_abs_path('.'.join([
        '-'.join([time_str, urllib.parse.quote(file_name, safe='')]),
        ext]))
    logger.info(f'Saving {file_name} to {data_folder} folder.')
    try:
        with createAndOpen(file_path, 'w') as exchange_file:
            file_content = str(json_content)
            exchange_file.write(file_content)
    except OSError as io_error:
        logger.exception(
            f'{time_str} - Error writing {file_name} file: {str(io_error)}')


def handle_subpages(html: str):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        class_name = auto_param_config('-c', '--class_name',
                                       help='subpages dom table class name')
        table = soup.find('table', {'class': class_name})
        links = table.find_all('a')
        logger.info(f'Subpages found: {len(links)}')
        subpages = map(
            lambda h: urllib.parse.urljoin(root_url, h.get('href')), links)
        for index, abs_href in enumerate(subpages):
            sub_html = fetch_url(abs_href)
            title = urllib.parse.quote(abs_href, safe='')
            save_html(sub_html, title)
            sub_sleep = random.randrange(sub_s_min, sub_s_max)
            logger.info(
                f'Sleep: {sub_sleep} s #{index}/{len(links)} ({abs_href})')
            time.sleep(sub_sleep)
    except Exception as e:
        logger.exception(str(e))


if __name__ == '__main__':
    if is_dev():
        logger.debug('Development machine: '
                     'While loop will break. Sleep time will be short.')
    while True:
        try:
            for i in range(max_pages):
                full_url = get_base_url()
                json_source = fetch_url(full_url)
                json_path = save_json(json_source, full_url)
                for_sleep = random.randrange(pg_s_min, pg_s_max)
                logger.info(f'Sleep: {for_sleep} s between base url (pages).')
                time.sleep(for_sleep)
        except Exception as e:
            logger.exception(str(e))
        finally:
            if is_dev():
                break;
            while_sleep = random.randrange(w_min, w_max)
            logger.info(f'Sleep: {while_sleep} s '
                        'between program run iterations.')
            time.sleep(while_sleep)
