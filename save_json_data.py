from bs4 import BeautifulSoup
import cachetools.func
import datetime
import logging
import logging.config
import random
import sys
import time
import urllib.request, urllib.error, urllib.parse
import yaml
from utils.auto_config_params_handler import auto_param_config
from utils.url_tools import fetch_url
from utils.file_tools import save_html, save_json


DEV_MACHINE = auto_param_config('-m', '--dev_machine',
                                help='development machine or platform')


def is_dev():
    return sys.platform == DEV_MACHINE


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
