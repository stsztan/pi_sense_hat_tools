from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
import pathlib
import datetime
import json
import os
import re
import configargparse


# globals
current_file = __file__
app = Flask(__name__)
CORS(app)


# consts
json_ext = '.json'
date_regex = r'\d{4}-\d{2}-\d{2}T\d{2}\.\d{2}\.\d{2}_\d*([+-]?\d{4})?'


# defaults
default_port = 9577
default_base_dir = 'data'
default_end_datetime = datetime.datetime.now()
default_start_datetime = default_end_datetime - datetime.timedelta(hours=1)


def config_param(param, *args, **kwargs):
    # handling configuration parameters
    config_file_stem = pathlib.Path(current_file).stem
    config_file = f'{config_file_stem}.conf'
    p = configargparse.ArgParser(
        default_config_files=[config_file]
    )
    p.add(*args, **kwargs)
    arg, unknown = p.parse_known_args()
    param = getattr(arg, param)
    return param


def merge_json(base_directory_path, start_datetime=None, end_datetime=None):
    merged_data = []
    # create full duirectory paths
    try:
        start_date = start_datetime.date()
    except AttributeError:
        start_datetime = default_start_datetime
        start_date = default_start_datetime.date()
    try:
        stop_date = end_datetime.date()
    except AttributeError:
        end_datetime = default_end_datetime
        stop_date = default_end_datetime.date()
    if start_date < stop_date:
        dates = [start_date + datetime.timedelta(days=d) 
                 for d in range((stop_date - start_date).days)
        ]
    else:
        dates = [stop_date]
    for directory_date in dates:
        directory_path = pathlib.Path.joinpath(
            pathlib.Path(base_directory_path),
            str(directory_date)
        )
        try:
            json_files = [
                f for f in os.listdir(directory_path)
                if os.path.splitext(f)[-1] == json_ext
            ]
        except FileNotFoundError as e:
            return f'Error: base/subdirectory/file may not exist: {str(e)}'
        for filename in json_files:
            file_path = os.path.join(directory_path, filename)
            pattern = re.compile(date_regex)
            groups = pattern.search(filename)
            if len(groups.regs) > 1:
                try:
                    file_time = (
                        datetime.datetime.strptime(
                            groups[0], '%Y-%m-%dT%H.%M.%S_%f'
                        )
                    )
                except Exception as e:
                    print(str(e))
            try:
                file_creation_time = file_time
            except NameError:
                file_creation_time = os.path.getctime(file_path)
            if start_datetime <= file_creation_time < end_datetime:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    merged_data.insert(0, data)
    return merged_data


@app.route("/json_content/<start_dt_str>/<end_dt_str>")
@cross_origin()
def retrieve_json_contents(start_dt_str, end_dt_str):
    # handling configuration parameters
    config_file_stem = pathlib.Path(current_file).stem
    p = configargparse.ArgParser(
        default_config_files=[f'{config_file_stem}.conf']
    )
    p.add('-d', '--directory', help='base folder path')
    args, unknown = p.parse_known_args()
    try:
        base_directory_path = args.directory
        if not os.path.isdir(base_directory_path):
            raise ValueError
    except (ValueError, TypeError):
        base_directory_path = default_base_dir
    # handling time range
    format_dt_str = '%Y-%m-%dT%H.%M.%S_%f'  # %z excluded, timezone: UTC
    try:
        start_datetime = datetime.datetime.strptime(
            start_dt_str, format_dt_str
        )
    except (ValueError, TypeError):
        start_datetime = default_start_datetime
    try:
        end_datetime = datetime.datetime.strptime(
            end_dt_str, format_dt_str
        )
    except (ValueError, TypeError):
        end_datetime = default_end_datetime
    # getting merged json
    json_data = merge_json(
        base_directory_path,
        start_datetime=start_datetime,
        end_datetime=end_datetime
    )
    try:
        return jsonify(json_data)  # json structure
    except Exception:
        try:
            return json_data  # data structure content (json/text)
        except Exception as e:
            return str(e)  # error string


if __name__ == '__main__':
    # handling configuration parameters
    port = config_param('port', '-p', '--port', help='listening port')
    try:
        port = int(port)
    except (ValueError, TypeError):
        port = default_port
    app.run(host='0.0.0.0', port=port)
