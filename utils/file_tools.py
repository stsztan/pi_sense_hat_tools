import datetime
import logging
import logging.config
import pathlib
import os
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


data_folder = auto_param_config('-d', '--data_folder',
                                help='data folder saving json')
default_encoding = auto_param_config('-e', '--encodings',
                                     help='default text/json encoding')
time_format = auto_param_config('-f', '--file_name_time_format',
                                help='default file name time'
                               ) or '%Y-%m-%dT%H.%M.%S_%f%z'


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


# TODO: common save_file
def save_html(html: str, url=''):
    safe_url = urllib.parse.quote(url, safe='')
    current_time = datetime.datetime.now().strftime(time_format)
    file_name = f'{safe_url}-{current_time}.html'
    file_path = get_abs_path(file_name)
    logger.info(file_path)
    try:
        with createAndOpen(file_path, 'w', encoding=default_encoding) as file:
            file.write(html)
        return str(file_path)
    except OSError as e:
        logger.exception(str(e))


# TODO: common save_file
def save_json(json_content: str, file_name: str, ext: str = 'json'):
    time_str = datetime.datetime.now().strftime(time_format)
    file_path = get_abs_path('.'.join([
        '-'.join([time_str, urllib.parse.quote(file_name, safe='')]),
        ext]))
    logger.info(f'Saving {file_name} to {data_folder} folder.')
    try:
        with createAndOpen(file_path, 'w') as file:
            file_content = str(json_content)
            file.write(file_content)
    except OSError as io_error:
        logger.exception(
            f'{time_str} - Error writing {file_name} file: {str(io_error)}')
