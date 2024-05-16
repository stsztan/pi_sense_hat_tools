import logging
import logging.config
import requests
import urllib.request, urllib.error, urllib.parse
import yaml
from utils.auto_config_params_handler import auto_param_config


try:
    with open('config.yml', 'r') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
except:
    logging.basicConfig(format='[%(levelname)s] %(process)d <%(name)s> '
                        '%(asctime)s | %(message)s', level=logging.DEBUG)

logger = logging.getLogger(__name__)


default_encoding = auto_param_config('-e', '--encodings',
                                     help='default text/json encoding'
                                    ) or 'UTF8'
root_url = auto_param_config('-r', '--url_root', help='url domain root')
base_url = auto_param_config('-b', '--url_base', help='base fetch url')
user_agent = auto_param_config('-u', '--user_agent',
                               help='fetch user agent text')


req_headers = {
 "headers": {
     "User-Agent": user_agent,
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


def fetch_url(url: str):
    try:
        logger.info(f'Fetching: {url}')
        response = requests.get(url, headers=req_headers['headers'])
        html_content = response.content.decode(default_encoding)
        return html_content
    except urllib.error.HTTPError as e:
        logger.exception(str(e))
        return e
